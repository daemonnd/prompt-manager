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
            self._write_to_file(command)
            return self._read_result(temp_file_path)
        finally:
            Path(temp_file_path).unlink()

    def _get_editor_command(self) -> list[str]:
        editor = os.environ.get("EDITOR")
        if editor is None:
            editor = "vim"
        return shlex.split(editor)

    def _write_to_file(self, command: list[str]):
        try:
            result = subprocess.run(args=command, check=True)
        except subprocess.CalledProcessError:
            raise EditorError(f"Failed to open editor for writing: {result.stderr}")

    def _read_result(self, temp_file_path) -> str:
        try:
            with open(temp_file_path, "r") as f:
                contents = f.read()
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            raise EditorError(str(e)) from e
        else:
            return contents
