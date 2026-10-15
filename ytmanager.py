#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# If not running in the project virtualenv where dependencies are installed,
# automatically re-execute using .venv/bin/python
_venv_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
if _venv_python.exists() and sys.executable != str(_venv_python):
	try:
		import tomli_w
		import click
		import PySide6
	except ImportError:
		os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

import click
from src.create import create
from src.save import load_settings
from src.status import status
from src.done import done
from src.cat import cat
from src.path import path


@click.command(help="Launch the Kirigami GUI application")
def gui() -> None:
	from src.gui.app import run_gui
	sys.exit(run_gui())


@click.group(invoke_without_command=True, help="Manages YouTube video Projects\n\nMade by IsaqueS")
@click.pass_context
def main(ctx: click.Context) -> None:
	if ctx.invoked_subcommand is None:
		from src.gui.app import run_gui
		sys.exit(run_gui())


main.add_command(gui)
main.add_command(create)
main.add_command(status)
main.add_command(done)
main.add_command(cat)
main.add_command(path)

if __name__ == "__main__":
	main()
