import click
from src.create import create
from src.save import load_settings
from src.status import status
from src.done import done
from src.cat import cat
from src.path import path

@click.group(help="Manages YouTube video Projects\n\nMade by IsaqueS")
def main() -> None:
	pass

main.add_command(create)
main.add_command(status)
main.add_command(done)
main.add_command(cat)
main.add_command(path)

if __name__ == "__main__":
	main()


