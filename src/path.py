import click, os, sys
from typing import Any
from pathlib import Path
from .save import settings, CURRENT_PROJECT_FILE_VERSION

@click.command(help="Prints the project path")
@click.option("-t", "--toml", help="Prints the project file path instead of the project directory path", is_flag=True)
@click.argument("projects", nargs = -1)
def path(projects, toml) -> None:
    if len(projects) == 0:
        click.echo(os.path.expanduser("/".join(settings["project"]["video-projects-folder"])) + "/") # HACK: will break on windows
        sys.exit(0)

    for project in projects:            
        project_file_name = settings["project"]["file-name"]
        projects_path: Path = Path() / os.path.expanduser("/".join(settings["project"]["video-projects-folder"]))
        
        toml_path: Path = projects_path / project / project_file_name

        if os.path.exists(toml_path):
            if toml:
                click.echo(str(toml_path))
            else:
                click.echo(str(projects_path / project) + "/") # HACK:It will break on windows! 
        else:
            click.secho(f"Project does not exist", fg="red")
