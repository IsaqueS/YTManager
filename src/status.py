import click, os, tomllib, sys
from typing import Any
from pathlib import Path
from .save import settings, CURRENT_PROJECT_FILE_VERSION

@click.command(help="Prints unfinished projects")
@click.option("-p", "--path", help="Prints the project path instead of the project name", is_flag=True)
def status(path) -> None:
    project_file_name = settings["project"]["file-name"]
    projects_path: Path = Path() / os.path.expanduser("/".join(settings["project"]["video-projects-folder"]))
    project_with_errors: list[str] = []
    projects: list = []

    for project in os.listdir(projects_path):
        project_path: Path = projects_path / project
        project_file_path = project_path / project_file_name
        if os.path.exists(project_file_path):
            with open(project_file_path, "rb") as file:
                try:
                    project_file:  dict[str, Any] = tomllib.load(file)
                    if project_file["id"] != project:
                        project_with_errors.append((project_file_path, f"ID ({project_file["id"]}) is not the same as the directory name ({project})"))
                    else:
                        projects.append(project_file)
                except tomllib.TOMLDecodeError as e:
                    project_with_errors.append((project_file_path, e))
                except KeyError:
                    project_with_errors.append((project_file_path, "Project file does not have id var"))
    
    if len(project_with_errors) > 0:
        click.secho(f"Found projects with toml errors:", fg="red", bold=True)
        for project in project_with_errors:
            click.secho(f"Path: {project[0]}\nError: {project[1]}", fg="red")

        sys.exit(1)
    
    for project in projects:
        if not project["metadata"]["video-uploaded"]:
            if path:
                click.echo(str(projects_path / project["id"]))
            else:
                click.echo(project["id"])