import tomllib
from tomllib import TOMLDecodeError
from prompt_manager.constants import PROMPT_TEMPLATES, PROMPTS_DIR
from prompt_manager.models import MetadataModel
from pydantic import ValidationError


def load_template(prompt_template: str):
    try:
        path = PROMPT_TEMPLATES / prompt_template
        with open(path, "rb") as f:
            return MetadataModel.model_validate(tomllib.load(f))
    except TOMLDecodeError as e:
        print(f"Unable to decode TOML in {path}: {str(e)}")
    except UnicodeDecodeError as e:
        print(f"Unable to decode TOML in {path}: {str(e)}")
    except IsADirectoryError as e:
        print(f"The config file is a directory: {str(e)}")
    except FileNotFoundError as e:
        print(f"The config file has not been found at {path}: {str(e)}")
    except PermissionError as e:
        print(f"Permission Error while opening the config file at {path}: {str(e)}")
    except ValidationError as e:
        print(f"The Config seems to be wrong: {str(e)}")


def load_prompt(prompt_file_name: str):
    try:
        path = PROMPTS_DIR / prompt_file_name
        with open(path, "r") as f:
            return f.read()
    except IsADirectoryError as e:
        raise
    except FileNotFoundError as e:
        raise
    except PermissionError as e:
        raise


if __name__ == "__main__":
    template = load_template("summary.toml")
    print(f"template: {template}")
    print("\n")
    print(f"prompt: {load_prompt(template.metadata.prompt_file_name)}")
