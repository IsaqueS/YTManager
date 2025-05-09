import click
from pathlib import Path
import os
import sys
from datetime import datetime
from .save import settings, CURRENT_PROJECT_FILE_VERSION

TOML_TEMPLATE = """# YTManager Project

version = "{version}" # Project file version (Not the cli version)
id = "{id}" # Must be the same as the folder name

[metadata]
date-of-creation = {date}
last-update = {date}
video-uploaded = false

[video]
title = "'{id}' title" # Must be <= 100 Characters
description = \"\"\"'{id}' description\"\"\" # Must be <= 4900 Characters
web-site = "('{id}' Link here)"
pre-web-site = "{pre_link}"
pre-description = "" # Text before description (ignored if empty) / Must be <= 45 Characters
pos-description = "" # Text after description (ignored if empty) / Must be <= 45 Characters

[path]
video-path = {video_path}
thumb-path = {thumb_path}

# Made by IsaqueS
"""

@click.command(help="Create video project(s). (To do multiple, separate by ',')")
@click.argument("projects", nargs=-1)
def create(projects) -> None:

	video_default_path: str = str(settings["default"]["path"]["video-path"])
	thumb_default_path: str = str(settings["default"]["path"]["thumb-path"])
	project_file_name: str = settings["project"]["file-name"]

	project_path: Path = Path()

	for path in settings["project"]["video-projects-folder"]:
		project_path = project_path / os.path.expanduser(path)
	
	folders: list[list[str]] = settings["project"]["folders"]

	temp_folders: list[list[str]] = []

	for folder in folders:
		spliced_path: list[str] = folder.split("/")
		temp_folders.append(spliced_path)
	
	folders = temp_folders
	del temp_folders

	# print(folders)

	if not os.path.exists(project_path):
		print(f"Path '{project_path}' does not exist!")
		sys.exit(1)

	counter = 1

	for project in projects:
		click.secho(f"{counter} - {project}", fg="blue", bold=True)
		counter += 1
		
		current_project_path: Path = project_path / project

		ignore_project: bool = False

		for folder in folders:

			folder_path = Path()

			for i in folder:
				folder_path = folder_path / i
			
			# print(folder_path)

			try:
				os.makedirs(current_project_path / folder_path)
			except FileExistsError:
				click.secho(f"Project '{project}' already exists!", fg="red")
				ignore_project = True
				break

			click.secho(f"folder '{folder_path}' was created")

		if ignore_project:
			continue

		date: datetime = datetime.now()

		project_toml_str = TOML_TEMPLATE.format(
			date = date.isoformat(),
			id = project,
			version = CURRENT_PROJECT_FILE_VERSION,
			video_path = video_default_path,
			thumb_path = thumb_default_path,
			pre_link = settings["default"]["description"].get("pre-link", "")
		)


		with open(current_project_path / project_file_name, "wt") as file:
			file.write(project_toml_str)
		
		click.secho(f"Project path: {current_project_path}", fg="magenta", bold=True)
		


