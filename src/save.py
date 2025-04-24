from pathlib import Path
from typing import Any
import click
import tomllib
import os
import sys

settings: dict[str, Any] = None

CURRENT_PROJECT_FILE_VERSION = "1.0.0"

SAVE_PATH: str = "save"

SETTINGS_FILE_NAME: str = "settings.toml"

def load_settings() -> None:
	file_path = Path(__file__).parent.parent / SAVE_PATH / SETTINGS_FILE_NAME

	if os.path.exists(file_path):
		with open(file_path, "rb") as file_data:
			try:
				global settings
				settings = tomllib.load(file_data)
			except tomllib.TOMLDecodeError as error:
				click.secho(f"Settings TOML file ({file_path}) has an parsing error!", fg="red", bold=True)
				click.secho(f"\nError:\n\t{error}", fg="red")
				sys.exit(1)
	else:
		click.secho(f"Settings file not found from: '{file_path}'", fg="red", bold=True)

	click.secho(f"Settings loaded from: '{file_path}'", bold=True, fg="green")

load_settings()