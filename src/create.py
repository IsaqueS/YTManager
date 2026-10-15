import click
from pathlib import Path
import os
import sys
from datetime import datetime
from .save import settings, CURRENT_PROJECT_FILE_VERSION, get_projects_folder_path

TOML_TEMPLATE = """# YTManager Project

version = "{version}" # Project file version (Not the cli version)
id = "{id}" # Must be the same as the folder name

[metadata]
date-of-creation = {date}
last-update = {date}
video-uploaded = false

[video]
title = {title} # Must be <= 100 Characters
description = \"\"\"{description}\"\"\" # Must be <= 4900 Characters
web-site = "{web_site}"
pre-web-site = "{pre_link}"
pre-description = "" # Text before description (ignored if empty) / Must be <= 45 Characters
pos-description = "" # Text after description (ignored if empty) / Must be <= 45 Characters

[path]
video-path = {video_path}
thumb-path = {thumb_path}

# Made by IsaqueS
"""

def create_project_directory(project: str, title: str = "", web_site: str = "") -> tuple[bool, str]:
	video_default_path: str = str(settings.get("default", {}).get("path", {}).get("video-path", ["Export", "Video"]))
	thumb_default_path: str = str(settings.get("default", {}).get("path", {}).get("thumb-path", ["Export", "Thumb"]))
	project_file_name: str = settings.get("project", {}).get("file-name", "project.toml")

	project_path: Path = get_projects_folder_path()

	folders: list[str] = settings.get("project", {}).get("folders", [])

	temp_folders: list[list[str]] = []
	for folder in folders:
		spliced_path: list[str] = folder.split("/")
		temp_folders.append(spliced_path)

	if not os.path.exists(project_path):
		try:
			os.makedirs(project_path, exist_ok=True)
		except Exception as e:
			return False, f"Path '{project_path}' does not exist and could not be created: {e}"

	current_project_path: Path = project_path / project

	for folder in temp_folders:
		folder_path = Path()
		for i in folder:
			folder_path = folder_path / i

		try:
			os.makedirs(current_project_path / folder_path)
		except FileExistsError:
			return False, f"Project '{project}' already exists!"
		except Exception as e:
			return False, f"Failed to create folder '{folder_path}': {e}"

	date: datetime = datetime.now()

	resolved_title = f"\"{title}\"" if title else f"\"{project}\""
	resolved_desc = f"'{project}' description"
	resolved_website = web_site if web_site else f"('{project}' Link here)"

	project_toml_str = TOML_TEMPLATE.format(
		date=date.isoformat(),
		id=project,
		version=CURRENT_PROJECT_FILE_VERSION,
		title=resolved_title,
		description=resolved_desc,
		web_site=resolved_website,
		video_path=video_default_path,
		thumb_path=thumb_default_path,
		pre_link=settings.get("default", {}).get("description", {}).get("pre-link", "")
	)

	with open(current_project_path / project_file_name, "wt") as file:
		file.write(project_toml_str)

	return True, str(current_project_path)

@click.command(help="Create video project(s). (To do multiple, separate by ',')")
@click.argument("projects", nargs=-1)
def create(projects) -> None:
	counter = 1
	for project in projects:
		click.secho(f"{counter} - {project}", fg="blue", bold=True)
		counter += 1
		success, msg = create_project_directory(project)
		if not success:
			click.secho(msg, fg="red")
		else:
			click.secho(f"Project path: {msg}", fg="magenta", bold=True)
