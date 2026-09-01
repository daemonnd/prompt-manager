import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Self

from prompt_manager.errors import EditorError


class EditorInput:
    """
    Class for getting input from an editor.
    Has to be used within a context manager.
    """

    def __enter__(self) -> Self:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
        ) as temp_file:
            self.temp_file_path = temp_file.name
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        Path(self.temp_file_path).unlink(missing_ok=True)

    def get_input(self) -> str:
        command = self._get_editor_command()
        command.append(self.temp_file_path)
        self._open_editor(command)
        return self._read_result(self.temp_file_path)

    def _get_editor_command(self) -> list[str]:
        editor = os.environ.get("EDITOR")
        if editor is None:
            editor = "vim"
        return shlex.split(editor)

    def _open_editor(self, command: list[str]):
        try:
            subprocess.run(
                args=command,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise EditorError(f"Failed to open editor for writing: {e!s}")

    def _read_result(self, temp_file_path) -> str:
        try:
            with open(temp_file_path, "r") as f:
                contents = f.read()
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            raise EditorError(str(e)) from e
        else:
            return contents
