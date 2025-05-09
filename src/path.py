import click, os, tomllib, sys
from typing import Any
from pathlib import Path
from .save import settings, CURRENT_PROJECT_FILE_VERSION

@click.command(help="Prints the project path")
@click.option("-t", "--toml", help="Prints the project file path instead of the project directory path", is_flag=True)
@click.argument("project", nargs = 1)
def path(project, toml) -> None:
    project_file_name = settings["project"]["file-name"]
    projects_path: Path = Path() / os.path.expanduser("/".join(settings["project"]["video-projects-folder"]))
    
    toml_path: Path = projects_path / project / project_file_name

    if os.path.exists(toml_path):
        if toml:
            click.echo(toml_path)
        else:
            click.echo(projects_path / project)
    else:
        click.secho(f"Project does not exist", fg="red")
