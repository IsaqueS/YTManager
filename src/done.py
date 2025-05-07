import click, os, tomli_w, tomllib, sys, datetime
from .save import settings, CURRENT_PROJECT_FILE_VERSION
from pathlib import Path

@click.command(help="Marks the video as done")
@click.argument("projects", nargs=-1)
@click.option("--all", "-a", is_flag=True, help="Loads all files from project directory")
def done(projects, all) -> None:
    project_file_name = settings["project"]["file-name"]
    path: Path = Path() / os.path.expanduser("/".join(settings["project"]["video-projects-folder"]))
    
    if all:
        projects = tuple(os.listdir(path))
    
    if len(projects) ==  0:
        click.secho(f"No arguments given", fg="red")
        sys.exit(1)

    for project in projects:
        if os.path.exists(path / project):
            project_file_path: Path = path / project / project_file_name

            try:
                file = open(project_file_path, "rb")
                
                project_file = tomllib.load(file)

                file.close()

                if project_file["metadata"]["video-uploaded"]:
                    continue

                project_file["metadata"]["video-uploaded"] = True
                project_file["metadata"]["last-update"] = datetime.datetime.now()

                new_project_file = tomli_w.dumps(project_file)

                file = open(project_file_path, "wt")
                file.write(new_project_file)
                file.close()

            except KeyError:
                click.secho(f"Project '{project}' toml file does not have the 'video-upload' var missing", fg="red")
            
        else:
            click.secho(f"Project '{project}' does not exist", fg="red")
        

