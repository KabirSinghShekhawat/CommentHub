"""Commenthub entry point script."""
from CommentHub import __cli_name__, default_parser_settings
from CommentHub.handlers import app
from core.parser import Parser
from core.remove import Remove
from core.dump_comments import StorageEngine
from pathlib import Path
import os
import fnmatch
import typer
import pyfiglet


def main():

    ascii_banner = pyfiglet.figlet_format("CommentHub")
    typer.echo(ascii_banner)

    app(prog_name=__cli_name__)


if __name__ == "__main__":
    main()
