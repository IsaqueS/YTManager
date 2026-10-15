import os
import subprocess
import tomllib
import tomli_w
from pathlib import Path
from typing import Any
from PySide6.QtCore import QUrl

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMAGE_SIZE = 15 * 1024 * 1024  # 15 MB limit

FINAL_THUMB_FILENAME = "thumbnail.webp"
PREVIEW_THUMB_FILENAME = "thumbnail_preview.webp"


def get_video_duration(video_path: Path) -> float:
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        val = res.stdout.strip()
        if val:
            return max(0.0, float(val))
    except Exception:
        pass
    return 0.0


def extract_middle_frame_to_webp(video_path: Path, output_webp: Path) -> bool:
    try:
        dur = get_video_duration(video_path)
        mid_time = dur / 2.0 if dur > 0 else 0.0

        output_webp.parent.mkdir(parents=True, exist_ok=True)
        temp_out = output_webp.with_suffix(".tmp.webp")

        cmd = [
            "ffmpeg",
            "-ss", f"{mid_time:.3f}",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "80",
            "-y",
            str(temp_out),
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=15)
        if res.returncode == 0 and temp_out.exists() and temp_out.stat().st_size > 0:
            temp_out.replace(output_webp)
            return True
        elif temp_out.exists():
            temp_out.unlink()
    except Exception:
        pass
    return False


def get_newest_exported_video(project_dir: Path, video_path_segments: list[str] | str | None) -> Path | None:
    candidate_dirs: list[Path] = []
    if video_path_segments:
        if isinstance(video_path_segments, list):
            target = project_dir
            for seg in video_path_segments:
                target = target / seg
            candidate_dirs.append(target)
        elif isinstance(video_path_segments, str):
            candidate_dirs.append(project_dir / video_path_segments)

    # Standard fallback export locations
    candidate_dirs.extend([
        project_dir / "Export" / "Video",
        project_dir / "Export",
    ])

    seen_dirs: set[Path] = set()
    found_videos: list[Path] = []
    for d in candidate_dirs:
        try:
            resolved = d.resolve()
        except Exception:
            continue
        if resolved in seen_dirs or not d.exists() or not d.is_dir():
            continue
        seen_dirs.add(resolved)
        for entry in d.iterdir():
            if entry.is_file() and entry.suffix.lower() in VIDEO_EXTENSIONS:
                found_videos.append(entry)

    if not found_videos:
        return None

    # Pick the newest by mtime
    found_videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found_videos[0]


def find_slides_image(project_dir: Path) -> Path | None:
    candidates = [
        project_dir / "Images" / "Slides",
        project_dir / "Slides",
    ]
    for d in candidates:
        if d.exists() and d.is_dir():
            imgs = [
                f for f in d.iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and f.stat().st_size <= MAX_IMAGE_SIZE
            ]
            if imgs:
                imgs.sort(key=lambda x: (not ("thumb" in x.stem.lower()), x.name.lower()))
                return imgs[0]
    return None


def find_images_image(project_dir: Path) -> Path | None:
    img_dir = project_dir / "Images"
    if img_dir.exists() and img_dir.is_dir():
        imgs = [
            f for f in img_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and f.stat().st_size <= MAX_IMAGE_SIZE
        ]
        if imgs:
            imgs.sort(key=lambda x: (not ("thumb" in x.stem.lower()), x.name.lower()))
            return imgs[0]
    return None


def find_biggest_video_in_project(project_dir: Path) -> Path | None:
    biggest: Path | None = None
    biggest_size = 0
    for root, _, files in os.walk(project_dir):
        root_path = Path(root)
        if "Export" in root_path.parts:
            continue
        for fn in files:
            ext = Path(fn).suffix.lower()
            if ext in VIDEO_EXTENSIONS:
                cand = root_path / fn
                try:
                    sz = cand.stat().st_size
                    if sz > biggest_size:
                        biggest_size = sz
                        biggest = cand
                except Exception:
                    pass
    return biggest


def save_toml_cache(toml_path: Path, cache_data: dict[str, Any]) -> None:
    try:
        if toml_path.exists():
            with open(toml_path, "rb") as f:
                doc = tomllib.load(f)
            doc["cache"] = cache_data
            with open(toml_path, "wt") as f:
                f.write(tomli_w.dumps(doc, multiline_strings=True))
    except Exception as e:
        print(f"Warning: could not save cache to {toml_path}: {e}")


def process_project_thumbnail(
    project_dir: Path,
    toml_data: dict[str, Any],
    toml_path: Path,
) -> str:
    cache = toml_data.get("cache")
    if not isinstance(cache, dict):
        cache = {}

    vpath_config = toml_data.get("path", {}).get("video-path")
    newest_exported_video = get_newest_exported_video(project_dir, vpath_config)

    # --- Priority 1: Video is ready and exported in Export folder ---
    if newest_exported_video is not None:
        final_thumb = project_dir / FINAL_THUMB_FILENAME
        preview_thumb = project_dir / PREVIEW_THUMB_FILENAME

        # If a non-finalized preview thumbnail existed, delete it now that video is complete
        if preview_thumb.exists():
            try:
                preview_thumb.unlink()
            except Exception:
                pass

        try:
            current_mtime = newest_exported_video.stat().st_mtime
            rel_vid = newest_exported_video.relative_to(project_dir).as_posix()
        except Exception:
            current_mtime = 0.0
            rel_vid = newest_exported_video.name

        cached_file = cache.get("final-video-file", "")
        cached_mtime = float(cache.get("final-video-mtime", 0.0) or 0.0)
        cache_type = cache.get("thumbnail-type", "")

        # Check if existing thumbnail.webp matches current newest video
        if (
            final_thumb.exists()
            and cached_file == rel_vid
            and abs(cached_mtime - current_mtime) < 1.0
            and cache_type == "final_video"
        ):
            return QUrl.fromLocalFile(str(final_thumb)).toString()

        # Generate or regenerate thumbnail.webp from the newest video
        extracted = extract_middle_frame_to_webp(newest_exported_video, final_thumb)
        if extracted and final_thumb.exists():
            cache["final-video-file"] = rel_vid
            cache["final-video-mtime"] = current_mtime
            cache["thumbnail-file"] = FINAL_THUMB_FILENAME
            cache["thumbnail-type"] = "final_video"
            # Remove any preview cache keys
            cache.pop("preview-video-file", None)
            cache.pop("preview-video-mtime", None)
            toml_data["cache"] = cache
            save_toml_cache(toml_path, cache)
            return QUrl.fromLocalFile(str(final_thumb)).toString()

    # --- Fallback 1: Slides folder image ---
    slides_img = find_slides_image(project_dir)
    if slides_img is not None:
        rel_img = slides_img.relative_to(project_dir).as_posix()
        if cache.get("thumbnail-file") != rel_img or cache.get("thumbnail-type") != "slides":
            cache["thumbnail-file"] = rel_img
            cache["thumbnail-type"] = "slides"
            toml_data["cache"] = cache
            save_toml_cache(toml_path, cache)
        return QUrl.fromLocalFile(str(slides_img)).toString()

    # --- Fallback 2: Images folder image ---
    images_img = find_images_image(project_dir)
    if images_img is not None:
        rel_img = images_img.relative_to(project_dir).as_posix()
        if cache.get("thumbnail-file") != rel_img or cache.get("thumbnail-type") != "images":
            cache["thumbnail-file"] = rel_img
            cache["thumbnail-type"] = "images"
            toml_data["cache"] = cache
            save_toml_cache(toml_path, cache)
        return QUrl.fromLocalFile(str(images_img)).toString()

    # --- Fallback 3: Frame on the middle of the biggest size raw video ---
    raw_video = find_biggest_video_in_project(project_dir)
    if raw_video is not None:
        preview_thumb = project_dir / PREVIEW_THUMB_FILENAME
        try:
            raw_mtime = raw_video.stat().st_mtime
            rel_raw = raw_video.relative_to(project_dir).as_posix()
        except Exception:
            raw_mtime = 0.0
            rel_raw = raw_video.name

        cached_file = cache.get("preview-video-file", "")
        cached_mtime = float(cache.get("preview-video-mtime", 0.0) or 0.0)
        cache_type = cache.get("thumbnail-type", "")

        if (
            preview_thumb.exists()
            and cached_file == rel_raw
            and abs(cached_mtime - raw_mtime) < 1.0
            and cache_type == "preview_video"
        ):
            return QUrl.fromLocalFile(str(preview_thumb)).toString()

        extracted = extract_middle_frame_to_webp(raw_video, preview_thumb)
        if extracted and preview_thumb.exists():
            cache["preview-video-file"] = rel_raw
            cache["preview-video-mtime"] = raw_mtime
            cache["thumbnail-file"] = PREVIEW_THUMB_FILENAME
            cache["thumbnail-type"] = "preview_video"
            toml_data["cache"] = cache
            save_toml_cache(toml_path, cache)
            return QUrl.fromLocalFile(str(preview_thumb)).toString()

    # --- Priority 5: Fallback to empty string (UI shows KDE video icon) ---
    return ""
