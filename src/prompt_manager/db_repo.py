import json
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, IntegrityError, OperationalError
from typing import Any, Generator, Literal

from pydantic import ValidationError

from prompt_manager.errors import (
    DBDataValidationError,
    DBIntegrityError,
    DBOperationalError,
    InternalDBError,
)
from prompt_manager.models import MetadataModel
from prompt_manager.paths import DATABASE_DIR


class PromptTemplateRepository:
    def __init__(self, db_path: Path = DATABASE_DIR) -> None:
        self.db_path: Path = db_path

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.open()
        self._initialize_database()

    def _initialize_database(self) -> None:
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS templates (
                name TEXT PRIMARY KEY,
                description TEXT,
                tags TEXT,
                prompt_file_name TEXT
            )
            """
        )
        self.conn.commit()

    def create_new(self, data: MetadataModel) -> None:
        """
        Method for adding a template to the database.
        """
        if isinstance(data.tags, list):
            raise InternalDBError(
                f"ValueError: data.tags cannot be a list for using with sqlite, but it is one: {data.tags}"
            )
        try:
            parameters: tuple = (
                data.name,
                data.description,
                data.tags,
                data.prompt_file_name,
            )
            self.cur.execute(
                """
                INSERT INTO templates VALUES
                (?, ?, ?, ?)
                """,
                parameters,
            )
            self.conn.commit()
        except IntegrityError as e:
            raise DBIntegrityError(
                f"IntegrityError: Failed to write to the database while creating template '{data.name}' because a database constraint was violated: {str(e)}"
            ) from e
        except OperationalError as e:
            raise DBOperationalError(
                f"Failed to write to the database while creating template '{data.name}' because of an operational error: {str(e)}"
            ) from e

    def update_template(self, name: str, data: MetadataModel) -> None:
        """
        Method to update an existing template.
        """
        if isinstance(data.tags, list):
            raise InternalDBError(
                f"ValueError: data.tags cannot be a list for using with sqlite, but it is one: {data.tags}"
            )
        try:
            parameters: tuple = (
                data.name,
                data.description,
                data.tags,
                data.prompt_file_name,
                name,
            )
            self.cur.execute(
                """
                UPDATE templates
                SET
                    name = ?,
                    description = ?,
                    tags = ?,
                    prompt_file_name = ?
                WHERE name = ?
                """,
                parameters,
            )
            self.conn.commit()

            if self.cur.rowcount != 1:
                print(
                    f"Expected to update 1 row for '{name}', updated {self.cur.rowcount}"
                )
        except IntegrityError as e:
            raise DBIntegrityError(
                f"Failed to write to the database while updating template '{data.name}' because a database constraint was violated: {str(e)}"
            ) from e
        except OperationalError as e:
            raise DBOperationalError(
                f"Failed to write to the database while updating template '{data.name}' because of an operational error: {str(e)}"
            ) from e

    def del_template(self, name: str) -> None:
        """
        Method to delete a template.
        """
        try:
            if not self.exists(name):
                raise InternalDBError(
                    f"ValueError: There is no template with the name '{name}' in the database."
                )

            self.cur.execute(
                """
                DELETE FROM templates
                WHERE name = ?
                """,
                (name,),
            )
            self.conn.commit()

            if self.cur.rowcount != 1:
                raise InternalDBError(
                    f"Expected to delete 1 row for '{name}', deleted {self.cur.rowcount}"
                )
        except IntegrityError as e:
            raise DBIntegrityError(
                f"Failed to write to the database while deleting template '{name}' because a database constraint was violated: {str(e)}"
            ) from e
        except OperationalError as e:
            raise DBOperationalError(
                f"Failed to write to the database while deleting template '{name}' because of an operational error: {str(e)}"
            ) from e

    def get(
        self,
        name: str,
    ) -> MetadataModel | None:
        """
        Method to get a template by name.
        """
        row = self.cur.execute(
            """
            SELECT * FROM templates
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        if row is None:
            return None

        try:
            return MetadataModel.model_validate(dict(row))
        except ValidationError as e:
            raise DBDataValidationError(
                f"The database seems to have invalid data: {str(e)}"
            ) from e

    def exists(self, name: str) -> bool:
        """
        Returns True if the template exists.
        """
        return (
            self.cur.execute(
                """
                SELECT 1 FROM templates
                WHERE name = ?
                """,
                (name,),
            ).fetchone()
            is not None
        )

    def get_all(self) -> Generator[MetadataModel, None, None]:
        """
        Method to iterate over all templates.
        """
        rows = self.cur.execute(
            """
            SELECT * FROM templates
            """
        ).fetchall()

        if not rows:
            return

        for row in rows:
            try:
                yield MetadataModel.model_validate(dict(row))
            except ValidationError as e:
                raise DBDataValidationError(
                    f"The database seems to have invalid data: {str(e)}"
                ) from e

    def list_templates(
        self,
        pattern: list[Literal["name", "description", "tags", "prompt_file_name"]],
    ) -> Generator[dict, None, None]:
        """
        Method to list the availible templates
        It returns a dict because it can explicitally return only some fields.
        Not recommended for internal usage, get_all is better for that.
        Used to display custom lists of the templates
        """
        search_pattern = ", ".join(pattern)
        templates = self.cur.execute(
            f"""
            SELECT {search_pattern} FROM templates
            """,
        ).fetchall()
        if not templates:
            return

        for extracted_pattern in templates:
            try:
                yield dict(extracted_pattern)
            except ValidationError as e:
                raise DBDataValidationError(
                    f"The database seems to have invalid data: {str(e)}"
                ) from e

    def get_template_name_by_prefix(self, prefix: str) -> Generator[str, None, None]:
        """
        Method to only return template names that match the prefix. used for autocompletion.
        """
        rows = self.cur.execute(
            """
            SELECT name
            FROM templates
            WHERE name LIKE ?
        """,
            (f"{prefix}%",),
        )

        for row in rows:
            yield row["name"]

    def remove_template(self, name: str) -> None:
        try:
            self.cur.execute(
                """
            DELETE FROM templates
            WHERE name = ?
            """,
                (name,),
            )
            self.conn.commit()

            if self.cur.rowcount != 1:
                raise InternalDBError(
                    f"Expected to delete 1 row for '{name}', deleted {self.cur.rowcount}"
                )
        except IntegrityError as e:
            raise DBIntegrityError(
                f"Failed to write to the database while deleting template '{name}' because a database constraint was violated: {str(e)}"
            ) from e
        except OperationalError as e:
            raise DBOperationalError(
                f"Failed to write to the database while deleting template '{name}' because of an operational error: {str(e)}"
            ) from e

    def close(self) -> None:
        self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """calls close(), for context managers"""
        self.close()

    def __enter__(self):
        """calls open(), for context manager"""
        self.close()  # close if it got opened by __init__
        self.open()
        return self

    def open(self) -> None:
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()
