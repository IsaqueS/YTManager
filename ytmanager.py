import click
from src.create import create
from src.save import load_settings

@click.group()
def main() -> None:
	pass

main.add_command(create)

if __name__ == "__main__":
	main()


