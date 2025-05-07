import click
from src.create import create
from src.save import load_settings
from src.status import status
from src.done import done

@click.group()
def main() -> None:
	pass

main.add_command(create)
main.add_command(status)
main.add_command(done)

if __name__ == "__main__":
	main()


