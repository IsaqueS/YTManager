import click, os, tomllib, sys
from typing import Any
from pathlib import Path
from .save import settings, CURRENT_PROJECT_FILE_VERSION

@click.command(help="Prints the information of an project")
@click.argument("project", nargs = 1)
def cat(project) -> None:
    project_file_name = settings["project"]["file-name"]
    projects_path: Path = Path() / os.path.expanduser("/".join(settings["project"]["video-projects-folder"]))
    
    toml_path: Path = projects_path / project / project_file_name

    if os.path.exists(toml_path):
        with open(toml_path,"rb") as file:
            data: dict[str, Any] = tomllib.load(file)
            output: str = ""

            string_to_add: str = data["video"].get("title", None)

            if isinstance(string_to_add, str) and len(string_to_add) > 0:
                output += f"{string_to_add}\n"
            
            string_to_add: str = data["video"].get("pre-description", None)

            if isinstance(string_to_add, str) and len(string_to_add) > 0:
                output += f"\n{string_to_add}\n"
            
            string_to_add: str = data["video"].get("description", None)

            if isinstance(string_to_add, str) and len(string_to_add) > 0:
                output += f"\n{string_to_add}\n"

            string_to_add: str = data["video"].get("pos-description", None)

            if isinstance(string_to_add, str) and len(string_to_add) > 0:
                output += f"\n{string_to_add}\n"
            
            pre_link: str = settings["default"]["description"].get("pre-link", "")
            pre_link = data["video"].get("pre-web-site", pre_link)
            
            web_site: str = data["video"].get("web-site", "")
            link: str = ""

            if len(web_site) > 0:
                if len(pre_link) > 0:
                    # print(link)
                    # print(pre_link)
                    link += pre_link
                link += web_site

                output += f"\n{link}"
            
            click.echo(output)
    else:
        click.secho(f"Project does not exist", fg="red")
