import tempfile
from pathlib import Path
import shlex
import os
import subprocess

from prompt_manager.errors import EditorError


class EditorInput:
    def __init__(self) -> None:
        pass

    def get_input(self) -> str:
        temp_file = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8")
        temp_file_path = temp_file.name
        try:
            command = self._get_editor_command()
            command.append(temp_file_path)
            print(f"command: {command}")
            self._open_editor(command)
            return self._read_result(temp_file_path)
        finally:
            Path(temp_file_path).unlink()

    def _get_editor_command(self) -> list[str]:
        editor = os.environ.get("EDITOR")
        if editor is None:
            editor = "vim"
        return shlex.split(editor)

    def _open_editor(self, command: list[str]):
        try:
            result = subprocess.run(args=command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise EditorError(f"Failed to open editor for writing: {str(e)}")

    def _read_result(self, temp_file_path) -> str:
        try:
            with open(temp_file_path, "r") as f:
                contents = f.read()
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            raise EditorError(str(e)) from e
        else:
            return contents
