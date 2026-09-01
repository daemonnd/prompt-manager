import tomllib
from tomllib import TOMLDecodeError

from pydantic import ValidationError

from prompt_manager.features.errors import PromptFileReadingError
from prompt_manager.models import MetadataModel
from prompt_manager.paths import PROMPT_TEMPLATES, PROMPTS_DIR


def load_template(prompt_template: str):
    try:
        path = PROMPT_TEMPLATES / prompt_template
        with open(path, "rb") as f:
            return MetadataModel.model_validate(tomllib.load(f))
    except TOMLDecodeError as e:
        print(f"Unable to decode TOML in {path}: {e!s}")
    except UnicodeDecodeError as e:
        print(f"Unable to decode TOML in {path}: {e!s}")
    except IsADirectoryError as e:
        print(f"The config file is a directory: {e!s}")
    except FileNotFoundError as e:
        print(f"The config file has not been found at {path}: {e!s}")
    except PermissionError as e:
        print(f"Permission Error while opening the config file at {path}: {e!s}")
    except ValidationError as e:
        print(f"The Config seems to be wrong: {e!s}")


def load_prompt(prompt_file_name: str):
    try:
        path = PROMPTS_DIR / prompt_file_name
        with open(path, "r") as f:
            return f.read()
    except (IsADirectoryError, FileNotFoundError, PermissionError) as e:
        raise PromptFileReadingError(
            f"Could no read prompt file '{path}': {e!s}"
        ) from e
