import datetime
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, IntegrityError, OperationalError
from typing import Generator, Literal

from platformdirs import user_data_dir
from pydantic import ValidationError

from prompt_manager.constants import DATABASE_DIR
from prompt_manager.models import MetadataModel


class VideoProcessingRepository:
    def __init__(self, db_path: Path = DATABASE_DIR) -> None:
        self.db_path: Path = db_path

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.open()
        self._initialize_database()

    def _initialize_database(self) -> None:
        self.cur.execute("""CREATE TABLE IF NOT EXISTS templates (
            name TEXT PRIMARY KEY,

            description TEXT,
            tags TEXT
            prompt_file_name TEXT
        )
        """)
        self.conn.commit()

    def create_new(self, data: MetadataModel):
        """
        Method for adding a template to the db.
        """
        try:
            parameters: tuple = (
                data.name,
                data.description,
                data.tags,
                data.prompt_file_name,
            )
            self.cur.execute(
                """
            INSERT INTO processed_videos VALUES
            (?, ?, ?, ?)""",
                parameters,
            )
            self.conn.commit()
        except IntegrityError as e:
            raise IntegrityError(
                f"IntegrityError: Failed to write to DB while creating template '{data.name}' because a database operand violated a constraint: {str(e)}"
            ) from e
        except OperationalError as e:
            raise OperationalError(
                f"Failed to write to DB while creating template '{data.name}' because of an operational Error: {str(e)}"
            ) from e

    def update_template(self, name: str, data: MetadataModel):
        """
        Method to add the validation data to the table entry and update the status to ether DONE, DOWNLOADING or SUMMARIZING
        """
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
                SET name = ?,
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
                    f"Expected to update 1 row for {name}, updated {self.cur.rowcount}"
                )
        except IntegrityError as e:
            raise IntegrityError(
                f"Failed to write to DB while updating the database entry for '{data.name}' the status after validation because a database operand violated a constraint: {str(e)}"
            ) from e
        except OperationalError as e:
            raise OperationalError(
                f"Failed to write to DB while updating the status after validation because of an operational Error: {str(e)}"
            ) from e

    def del_row(self, name: str):
        """
        Method to delete a row so that the video can later be processed again
        """
        try:
            if not self.exists(name):
                raise ValueError(
                    f"There is no row with the video id {name} in the database, it cannot be removed"
                )

            self.cur.execute(
                """
                DELETE FROM processed_videos
                WHERE video_id = ?
                """,
                (name,),
            )
            self.conn.commit()
            if self.cur.rowcount != 1:
                raise Exception(
                    f"Expected to update 1 row for {name}, updated {self.cur.rowcount}"
                )
        except IntegrityError as e:
            raise IntegrityError(
                f"Failed to write to DB while deleting row with name '{name}' because a database operand violated a constraint: {str(e)}"
            )
        except OperationalError as e:
            raise OperationalError(
                f"Failed to write to DB while deleting row with name '{name}' because of an operational Error: {str(e)}"
            ) from e

    def get(self, video_id: str) -> VideoProcessingRecord | None:
        """
        Method to get the DB entry of the video with the video id video_id.
        """
        row = self.cur.execute(
            "SELECT * FROM processed_videos WHERE video_id=?", (video_id,)
        ).fetchone()
        if row is None:
            return None
        try:
            return VideoProcessingRecord.model_validate(dict(row))
        except ValidationError as e:
            raise VideoProcessingDataValidationError(
                f"Failed to return results because of a ValidationError from pydantic: {str(e)}"
            ) from e

    def exists(self, video_id: str) -> bool:
        """
        Method to get if an entry already exists
        Returns True if it already exists
        Returns False if it does not exist
        """
        if (
            self.cur.execute(
                "SELECT 1 FROM processed_videos WHERE video_id=?", (video_id,)
            )
        ).fetchone():
            return True
        else:
            return False

    def get_by_status(
        self,
        status: Literal[
            "downloading",
            "summarizing",
            "done",
            "failed",
            "validating",
            "livestream_checking",
        ],
    ) -> Generator[VideoProcessingRecord, None, None]:
        """
        Method to get a list of the videos interrupted
        """
        parameters: tuple = (status,)
        rows = self.cur.execute(
            """
        SELECT * FROM processed_videos
        WHERE status = ?
        """,
            parameters,
        ).fetchall()
        if not rows:
            return None
        for row in rows:
            try:
                yield VideoProcessingRecord.model_validate(dict(row))
            except ValidationError as e:
                raise VideoProcessingDataValidationError(
                    f"Failed to get the data of a video because of a ValidationError, database seems corrupt: {str(e)}"
                ) from e

    def get_by_channelid(
        self, channel_id: str
    ) -> Generator[VideoProcessingRecord, None, None]:
        parameters: tuple = (channel_id,)
        rows = self.cur.execute(
            """
        SELECT * FROM processed_videos
        WHERE channel_id = ?
        """,
            parameters,
        ).fetchall()
        if not rows:
            return None
        for row in rows:
            try:
                yield VideoProcessingRecord.model_validate(dict(row))
            except ValidationError as e:
                raise VideoProcessingDataValidationError(
                    f"Failed to get the data of a video because of a ValidationError, database seems corrupt: {str(e)}"
                ) from e

    def get_all(self) -> Generator[VideoProcessingRecord, None, None]:
        rows = self.cur.execute("""
        SELECT * FROM processed_videos
        """).fetchall()
        if not rows:
            return None
        for row in rows:
            try:
                yield VideoProcessingRecord.model_validate(dict(row))
            except ValidationError as e:
                raise VideoProcessingDataValidationError(
                    f"Failed to get the data of a video because of a ValidationError, database seems corrupt: {str(e)}"
                ) from e

    def set_status(
        self, video_id: str, status: VideoProcessingStatus, reset_attempts: bool = False
    ) -> None:
        """
        Method to edit the status of a video
        """
        if reset_attempts:
            retry_count = 0
        else:
            result = self.cur.execute(
                """
            SELECT retry_count FROM processed_videos
            WHERE video_id = ?
            """,
                (video_id,),
            ).fetchone()
            if result:
                retry_count = result[0]
            else:
                retry_count = 0

        try:
            parameters: tuple = (status.value, int(retry_count), video_id)
            self.cur.execute(
                """
            UPDATE processed_videos
            SET status = ?,
            retry_count = ?
            WHERE video_id = ?;
            """,
                parameters,
            )
            self.conn.commit()
        except IntegrityError as e:
            raise DBWritingError(
                f"Failed to write to DB while updating the status to {status} for {video_id} because a database operand violated a constraint: {str(e)}"
            )
        except OperationalError as e:
            raise DBWritingError(
                f"Failed to write to DB while updating the status to {status} for {video_id} because of an operational Error: {str(e)}"
            ) from e

    def close(self) -> None:
        self.conn.close()

    def open(self) -> None:
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()


if __name__ == "__main__":
    vcr = VideoProcessingRepository()
    vid: Video = Video(
        title="sometitle",
        url="someurl",
        author="randomauthor",
        published="someday",
        video_id="ai90a7di7hk",
        channel_id="somechannelid",
    )

    vcr.create(vid=vid)
    result = vcr.get("ai90a7di7hk")
    print(result)
