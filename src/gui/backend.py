import os
import sys
import tomllib
import tomli_w
from pathlib import Path
from datetime import datetime, date
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtGui import QGuiApplication, QDesktopServices
from PySide6.QtWidgets import QFileDialog

from ..save import (
    settings,
    load_settings,
    save_settings_file,
    get_projects_folder_path,
    CURRENT_PROJECT_FILE_VERSION,
)
from ..create import create_project_directory

MAX_THUMBNAIL_BYTES = 15 * 1024 * 1024  # 15 MB limit to avoid huge print rendering files


def format_dt(dt: Any) -> tuple[str, str]:
    if isinstance(dt, (datetime, date)):
        iso = dt.isoformat()
        formatted = dt.strftime("%d/%m/%Y %H:%M") if isinstance(dt, datetime) else dt.strftime("%d/%m/%Y")
        return iso, formatted
    if isinstance(dt, str):
        try:
            d = datetime.fromisoformat(dt)
            return dt, d.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return dt, dt
    return "", ""


def path_to_folder_parts(folder_path: str) -> list[str]:
    home = os.path.expanduser("~")
    abs_path = os.path.abspath(os.path.expanduser(folder_path))
    if abs_path.startswith(home):
        rel = os.path.relpath(abs_path, home)
        if rel == ".":
            return ["~"]
        parts = rel.split(os.sep)
        return ["~"] + [p for p in parts if p]
    parts = [part for part in abs_path.split(os.sep) if part]
    if parts:
        return ["/" + parts[0]] + parts[1:]
    return ["/"]


def build_formatted_youtube_text(data: dict[str, Any], default_pre_link: str = "") -> str:
    video_sec = data.get("video", {})
    output_parts: list[str] = []

    title = video_sec.get("title", "")
    if isinstance(title, str) and title.strip():
        output_parts.append(title.strip())

    pre_desc = video_sec.get("pre-description", "")
    if isinstance(pre_desc, str) and pre_desc.strip():
        output_parts.append(pre_desc.strip())

    desc = video_sec.get("description", "")
    if isinstance(desc, str) and desc.strip():
        output_parts.append(desc.strip())

    pos_desc = video_sec.get("pos-description", "")
    if isinstance(pos_desc, str) and pos_desc.strip():
        output_parts.append(pos_desc.strip())

    pre_link = video_sec.get("pre-web-site", default_pre_link)
    web_site = video_sec.get("web-site", "")
    if isinstance(web_site, str) and web_site.strip():
        link_str = ""
        if pre_link and isinstance(pre_link, str):
            link_str += pre_link
        link_str += web_site.strip()
        output_parts.append(link_str)

    return "\n\n".join(output_parts)


class ProjectBackend(QObject):
    projectsChanged = Signal()
    settingsChanged = Signal()
    activeProjectChanged = Signal()
    notification = Signal(str, bool)  # message, is_error

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._projects: list[dict[str, Any]] = []
        self._active_project: dict[str, Any] = {}
        self._settings_data: dict[str, Any] = {}
        self.loadSettingsData()
        self.reloadProjects()

    # --- Properties ---

    @Property("QVariantList", notify=projectsChanged)
    def projects(self) -> list[dict[str, Any]]:
        return self._projects

    @Property("QVariantMap", notify=activeProjectChanged)
    def activeProject(self) -> dict[str, Any]:
        return self._active_project

    @Property(int, notify=projectsChanged)
    def totalCount(self) -> int:
        return len(self._projects)

    @Property(int, notify=projectsChanged)
    def inProgressCount(self) -> int:
        return sum(1 for p in self._projects if not p.get("videoUploaded", False))

    @Property(int, notify=projectsChanged)
    def uploadedCount(self) -> int:
        return sum(1 for p in self._projects if p.get("videoUploaded", False))

    @Property(str, notify=settingsChanged)
    def projectsFolder(self) -> str:
        return str(get_projects_folder_path())

    @Property("QVariantMap", notify=settingsChanged)
    def settingsData(self) -> dict[str, Any]:
        return self._settings_data

    # --- Slots ---

    @Slot()
    def loadSettingsData(self) -> None:
        st = load_settings()
        self._settings_data = {
            "videoProjectsFolder": str(get_projects_folder_path()),
            "fileName": st.get("project", {}).get("file-name", "project.toml"),
            "folders": st.get("project", {}).get("folders", []),
            "defaultVideoPath": "/".join(st.get("default", {}).get("path", {}).get("video-path", ["Export", "Video"])),
            "defaultThumbPath": "/".join(st.get("default", {}).get("path", {}).get("thumb-path", ["Export", "Thumb"])),
            "defaultPreLink": st.get("default", {}).get("description", {}).get("pre-link", "Saiba mais: "),
        }
        self.settingsChanged.emit()

    @Slot()
    def reloadProjects(self) -> None:
        projects_path = get_projects_folder_path()
        st = load_settings()
        file_name = st.get("project", {}).get("file-name", "project.toml")
        default_pre_link = st.get("default", {}).get("description", {}).get("pre-link", "")

        projects: list[dict[str, Any]] = []

        if not os.path.exists(projects_path):
            self._projects = []
            self.projectsChanged.emit()
            return

        try:
            entries = sorted(os.listdir(projects_path))
        except Exception as e:
            self.notification.emit(f"Failed to read projects folder: {e}", True)
            self._projects = []
            self.projectsChanged.emit()
            return

        for entry in entries:
            p_dir = projects_path / entry
            if not p_dir.is_dir():
                continue

            toml_file = p_dir / file_name
            if not toml_file.exists():
                continue

            try:
                with open(toml_file, "rb") as f:
                    data = tomllib.load(f)
            except Exception as e:
                projects.append({
                    "id": entry,
                    "title": f"[Error loading {entry}]",
                    "description": f"TOML Error: {e}",
                    "preDescription": "",
                    "posDescription": "",
                    "webSite": "",
                    "preWebSite": "",
                    "videoUploaded": False,
                    "dateOfCreation": "",
                    "lastUpdate": "",
                    "formattedDate": "",
                    "videoPath": "Export/Video",
                    "thumbPath": "Export/Thumb",
                    "thumbnailUrl": "",
                    "fullPath": str(p_dir),
                    "tomlPath": str(toml_file),
                    "formattedText": "",
                    "hasError": True,
                    "errorMessage": str(e),
                })
                continue

            meta = data.get("metadata", {})
            video = data.get("video", {})
            paths = data.get("path", {})

            # Dates
            created_iso, created_fmt = format_dt(meta.get("date-of-creation"))
            update_iso, update_fmt = format_dt(meta.get("last-update"))

            # Paths
            vpath_raw = paths.get("video-path", ["Export", "Video"])
            tpath_raw = paths.get("thumb-path", ["Export", "Thumb"])

            vpath_str = "/".join(vpath_raw) if isinstance(vpath_raw, list) else str(vpath_raw)
            tpath_str = "/".join(tpath_raw) if isinstance(tpath_raw, list) else str(tpath_raw)

            # Resolve thumbnail file
            thumb_url = ""
            thumb_folder = p_dir
            if isinstance(tpath_raw, list):
                for seg in tpath_raw:
                    thumb_folder = thumb_folder / seg
            else:
                thumb_folder = thumb_folder / str(tpath_raw)

            if thumb_folder.exists() and thumb_folder.is_dir():
                try:
                    thumb_files = os.listdir(thumb_folder)
                    preferred = ["thumb.png", "Thumb.png", "thumb.jpg", "Thumb.jpg", "thumb.jpeg", "thumbnail.png"]
                    chosen = None
                    for pref in preferred:
                        if pref in thumb_files:
                            cand = thumb_folder / pref
                            if cand.stat().st_size <= MAX_THUMBNAIL_BYTES:
                                chosen = cand
                                break
                    if not chosen:
                        for fn in thumb_files:
                            if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                                cand = thumb_folder / fn
                                if cand.stat().st_size <= MAX_THUMBNAIL_BYTES:
                                    chosen = cand
                                    break
                    if chosen:
                        thumb_url = QUrl.fromLocalFile(str(chosen)).toString()
                except Exception:
                    pass

            # Fallback search if still not found
            if not thumb_url:
                for fallback_dir_name in ["Export", "Images"]:
                    fb = p_dir / fallback_dir_name
                    if fb.exists() and fb.is_dir():
                        try:
                            for root, _, files in os.walk(fb):
                                for fn in files:
                                    if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                                        cand = Path(root) / fn
                                        if cand.stat().st_size <= MAX_THUMBNAIL_BYTES:
                                            thumb_url = QUrl.fromLocalFile(str(cand)).toString()
                                            break
                                if thumb_url:
                                    break
                        except Exception:
                            pass
                    if thumb_url:
                        break

            # Check if video export exists
            has_video_export = False
            video_folder = p_dir
            if isinstance(vpath_raw, list):
                for seg in vpath_raw:
                    video_folder = video_folder / seg
            if video_folder.exists() and video_folder.is_dir():
                try:
                    for vf in os.listdir(video_folder):
                        if vf.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
                            has_video_export = True
                            break
                except Exception:
                    pass

            formatted_text = build_formatted_youtube_text(data, default_pre_link)

            project_item = {
                "id": str(data.get("id", entry)),
                "title": str(video.get("title", "")),
                "description": str(video.get("description", "")),
                "preDescription": str(video.get("pre-description", "")),
                "posDescription": str(video.get("pos-description", "")),
                "webSite": str(video.get("web-site", "")),
                "preWebSite": str(video.get("pre-web-site", default_pre_link)),
                "videoUploaded": bool(meta.get("video-uploaded", False)),
                "dateOfCreation": created_iso,
                "lastUpdate": update_iso,
                "formattedDate": update_fmt or created_fmt,
                "videoPath": vpath_str,
                "thumbPath": tpath_str,
                "thumbnailUrl": thumb_url,
                "fullPath": str(p_dir),
                "tomlPath": str(toml_file),
                "formattedText": formatted_text,
                "hasVideoExport": has_video_export,
                "hasError": False,
                "errorMessage": "",
            }
            projects.append(project_item)

        def sort_key(p: dict[str, Any]):
            return p.get("lastUpdate", "") or ""

        projects.sort(key=sort_key, reverse=True)
        self._projects = projects
        self.projectsChanged.emit()

        if self._active_project:
            act_id = self._active_project.get("id")
            for p in self._projects:
                if p.get("id") == act_id:
                    self._active_project = p
                    self.activeProjectChanged.emit()
                    break

    @Slot(str)
    def selectProject(self, project_id: str) -> None:
        for p in self._projects:
            if p.get("id") == project_id:
                self._active_project = p
                self.activeProjectChanged.emit()
                return

    @Slot(str, bool, result=bool)
    def setUploaded(self, project_id: str, uploaded: bool) -> bool:
        projects_path = get_projects_folder_path()
        st = load_settings()
        file_name = st.get("project", {}).get("file-name", "project.toml")
        toml_path = projects_path / project_id / file_name

        if not toml_path.exists():
            self.notification.emit(f"Project '{project_id}' file not found!", True)
            return False

        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)

            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["video-uploaded"] = uploaded
            data["metadata"]["last-update"] = datetime.now()

            with open(toml_path, "wt") as f:
                f.write(tomli_w.dumps(data, multiline_strings=True))

            status_str = "Uploaded" if uploaded else "In Progress"
            self.notification.emit(f"Project '{project_id}' marked as {status_str}.", False)
            self.reloadProjects()
            return True
        except Exception as e:
            self.notification.emit(f"Failed to update project: {e}", True)
            return False

    @Slot(str, str, str, str, str, str, str, bool, str, str, result=bool)
    def saveProject(
        self,
        project_id: str,
        title: str,
        description: str,
        pre_desc: str,
        pos_desc: str,
        pre_web_site: str,
        web_site: str,
        uploaded: bool,
        video_path_str: str,
        thumb_path_str: str,
    ) -> bool:
        projects_path = get_projects_folder_path()
        st = load_settings()
        file_name = st.get("project", {}).get("file-name", "project.toml")
        toml_path = projects_path / project_id / file_name

        if not toml_path.exists():
            self.notification.emit(f"Project '{project_id}' file not found!", True)
            return False

        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)

            if "metadata" not in data:
                data["metadata"] = {}
            if "video" not in data:
                data["video"] = {}
            if "path" not in data:
                data["path"] = {}

            data["video"]["title"] = title
            data["video"]["description"] = description
            data["video"]["pre-description"] = pre_desc
            data["video"]["pos-description"] = pos_desc
            data["video"]["pre-web-site"] = pre_web_site
            data["video"]["web-site"] = web_site

            data["metadata"]["video-uploaded"] = uploaded
            data["metadata"]["last-update"] = datetime.now()

            v_segments = [s.strip() for s in video_path_str.replace("\\", "/").split("/") if s.strip()]
            t_segments = [s.strip() for s in thumb_path_str.replace("\\", "/").split("/") if s.strip()]

            data["path"]["video-path"] = v_segments or ["Export", "Video"]
            data["path"]["thumb-path"] = t_segments or ["Export", "Thumb"]

            with open(toml_path, "wt") as f:
                f.write(tomli_w.dumps(data, multiline_strings=True))

            self.notification.emit(f"Project '{project_id}' saved successfully!", False)
            self.reloadProjects()
            self.selectProject(project_id)
            return True
        except Exception as e:
            self.notification.emit(f"Failed to save project '{project_id}': {e}", True)
            return False

    @Slot(str, str, str, result=bool)
    def createProject(self, project_id: str, title: str, web_site: str) -> bool:
        project_id = project_id.strip()
        if not project_id:
            self.notification.emit("Project ID cannot be empty!", True)
            return False

        success, msg = create_project_directory(project_id, title=title.strip(), web_site=web_site.strip())
        if not success:
            self.notification.emit(msg, True)
            return False

        self.notification.emit(f"Project '{project_id}' created successfully!", False)
        self.reloadProjects()
        self.selectProject(project_id)
        return True

    @Slot(str)
    def openFolder(self, folder_path: str) -> None:
        if os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            self.notification.emit(f"Folder '{folder_path}' does not exist!", True)

    @Slot(str)
    def openProjectFolder(self, project_id: str) -> None:
        projects_path = get_projects_folder_path()
        target = projects_path / project_id
        self.openFolder(str(target))

    @Slot(str)
    def openThumbFolder(self, project_id: str) -> None:
        projects_path = get_projects_folder_path()
        for p in self._projects:
            if p.get("id") == project_id:
                tpath = p.get("thumbPath", "Export/Thumb")
                target = projects_path / project_id
                for seg in tpath.split("/"):
                    target = target / seg
                if not target.exists():
                    os.makedirs(target, exist_ok=True)
                self.openFolder(str(target))
                return
        target = projects_path / project_id / "Export" / "Thumb"
        if not target.exists():
            os.makedirs(target, exist_ok=True)
        self.openFolder(str(target))

    @Slot(str)
    def openVideoFolder(self, project_id: str) -> None:
        projects_path = get_projects_folder_path()
        for p in self._projects:
            if p.get("id") == project_id:
                vpath = p.get("videoPath", "Export/Video")
                target = projects_path / project_id
                for seg in vpath.split("/"):
                    target = target / seg
                if not target.exists():
                    os.makedirs(target, exist_ok=True)
                self.openFolder(str(target))
                return
        target = projects_path / project_id / "Export" / "Video"
        if not target.exists():
            os.makedirs(target, exist_ok=True)
        self.openFolder(str(target))

    @Slot(str)
    def copyToClipboard(self, text: str) -> None:
        cb = QGuiApplication.clipboard()
        if cb:
            cb.setText(text)
            self.notification.emit("Copied to clipboard!", False)

    @Slot(str, result=str)
    def chooseFolder(self, current_dir: str = "") -> str:
        start_dir = current_dir if current_dir and os.path.exists(current_dir) else str(get_projects_folder_path())
        selected = QFileDialog.getExistingDirectory(
            None,
            "Select Video Projects Folder",
            start_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        return selected

    @Slot(str, str, str, str, str, "QVariantList", result=bool)
    def saveSettings(
        self,
        folder_path: str,
        file_name: str,
        default_video_path: str,
        default_thumb_path: str,
        default_pre_link: str,
        folders_list: list[str],
    ) -> bool:
        try:
            folder_parts = path_to_folder_parts(folder_path)
            v_segments = [s.strip() for s in default_video_path.replace("\\", "/").split("/") if s.strip()]
            t_segments = [s.strip() for s in default_thumb_path.replace("\\", "/").split("/") if s.strip()]

            new_settings = {
                "project": {
                    "folders": [str(f).strip() for f in folders_list if str(f).strip()],
                    "video-projects-folder": folder_parts,
                    "file-name": file_name.strip() or "project.toml",
                },
                "default": {
                    "path": {
                        "video-path": v_segments or ["Export", "Video"],
                        "thumb-path": t_segments or ["Export", "Thumb"],
                    },
                    "description": {
                        "pre-link": default_pre_link,
                    },
                },
            }

            save_settings_file(new_settings)
            self.loadSettingsData()
            self.reloadProjects()
            self.notification.emit("Settings saved successfully!", False)
            return True
        except Exception as e:
            self.notification.emit(f"Failed to save settings: {e}", True)
            return False
