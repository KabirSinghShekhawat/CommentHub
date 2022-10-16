from click import version_option
import typer
from typing import Optional

from CommentHub import __cli_name__, __version__, default_parser_settings

from models import models
from db.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


import os
import fnmatch
from pathlib import Path
from core.dump_comments import StorageEngine
from controllers.DbCrudController import DbCrudController
from models.serializers import FileCreate, File, Version

app = typer.Typer()

from core.parser import Parser
from core.remove import Remove
import pprint


def parse_project(parser, cwd: str = os.getcwd()):
    if not os.path.exists(".comment_hub"):
        os.mkdir(".comment_hub")

    db = DbCrudController(get_db())

    for (root, _, files) in os.walk(cwd):
        files = fnmatch.filter(files, "*.py")
        for file_name in files:
            source_file_path = Path(root, file_name)
            file_id = db.get_file_id(str(source_file_path))

            if not file_id:
                db.create_file(FileCreate(location=str(source_file_path)))
                file_id = db.get_file_id(str(source_file_path))

            if not file_id:
                raise Exception(f"file not found: {str(source_file_path)}")

            versionObj = db.get_latest_file_version(file_id)
            version = versionObj.version + 1 if versionObj else 1

            comments = parser.parse(source_file_path)
            storage_engine = StorageEngine(version + 1, cwd, file_id)
            file_loc = storage_engine.dump(comments)

            if not file_loc:
                continue

            newVersion = Version(
                version=version, file_id=file_id, location=str(file_loc)
            )
            db.create_file_version(newVersion)

            Remove.remove_comments(source_file_path, comments)


@app.command()
def remove_comments(file_location: Optional[str] = typer.Argument(None)):
    """Remove commented out code under comment-tag"""
    parser = Parser()
    parser.load_parser_settings(default_parser_settings)
    if file_location:
        parse_project(parser, file_location)
    else:
        parse_project(parser)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__cli_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
