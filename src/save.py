from pathlib import Path
from typing import Any
import click
import tomllib
import tomli_w
import os
import sys

settings: dict[str, Any] = {}

CURRENT_PROJECT_FILE_VERSION = "1.1.0"

SAVE_PATH: str = "save"

SETTINGS_FILE_NAME: str = "settings.toml"

def get_settings_file_path() -> Path:
	return Path(__file__).parent.parent / SAVE_PATH / SETTINGS_FILE_NAME

def load_settings() -> dict[str, Any]:
	global settings
	file_path = get_settings_file_path()

	if os.path.exists(file_path):
		with open(file_path, "rb") as file_data:
			try:
				settings = tomllib.load(file_data)
				return settings
			except tomllib.TOMLDecodeError as error:
				click.secho(f"Settings TOML file ({file_path}) has an parsing error!", fg="red", bold=True)
				click.secho(f"\nError:\n\t{error}", fg="red")
				if "pytest" not in sys.modules:
					sys.exit(1)
	else:
		click.secho(f"Settings file not found from: '{file_path}'", fg="red", bold=True)
	return settings

def save_settings_file(new_settings: dict[str, Any]) -> None:
	global settings
	file_path = get_settings_file_path()
	os.makedirs(file_path.parent, exist_ok=True)
	with open(file_path, "wt") as file_data:
		file_data.write(tomli_w.dumps(new_settings, multiline_strings=True))
	settings = new_settings

def get_projects_folder_path() -> Path:
	global settings
	if not settings:
		load_settings()
	project_path: Path = Path()
	for p in settings.get("project", {}).get("video-projects-folder", ["~", "Vídeos", "VideosEvolução"]):
		project_path = project_path / os.path.expanduser(p)
	return project_path

load_settings()
