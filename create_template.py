from models import MetadataModel, PromptTemplateModel
from pathlib import Path
import toml
from constants import PROMPT_TEMPLATES, PROMPTS_DIR


def get_data() -> PromptTemplateModel:
    """
    Function that returns the metadata of the template as
    template data model and the template prompt as str
    """
    name = input("How should the new prompt template be called? ")
    description = input(f"How would you describe the new prompt template '{name}'? ")
    tags = input(
        f"Which tags should the new prompt template '{name}' get? Format: 'summary,transcript,video'"
    ).split(",")
    prompt_file_name = f"{name}.md"
    prompt = input("Enter the prompt template, use '{}' for variables: ")
    return PromptTemplateModel(
        name=name,
        description=description,
        tags=tags,
        prompt_file_name=prompt_file_name,
        prompt=prompt,
    )


def save_template(data: PromptTemplateModel):
    prompt_template_path: Path = PROMPT_TEMPLATES / f"{data.name}.toml"
    try:
        with open(prompt_template_path, "w") as f:
            f.write(toml.dumps(MetadataModel.from_template(data).model_dump()))
    except UnicodeDecodeError as e:
        print(f"Unable to decode TOML in {prompt_template_path}: {str(e)}")
    except IsADirectoryError as e:
        print(f"The config file is a directory: {str(e)}")
    except FileNotFoundError as e:
        print(f"The config file has not been found at {prompt_template_path}: {str(e)}")
    except PermissionError as e:
        print(
            f"Permission Error while opening the config file at {prompt_template_path}: {str(e)}"
        )

    prompt_path: Path = PROMPTS_DIR / data.prompt_file_name
    try:
        with open(prompt_path, "w") as f:
            f.write(data.prompt)
    except IsADirectoryError as e:
        print(f"The config file is a directory: {str(e)}")
    except FileNotFoundError as e:
        print(f"The config file has not been found at {prompt_path}: {str(e)}")
    except PermissionError as e:
        print(
            f"Permission Error while opening the config file at {prompt_path}: {str(e)}"
        )


if __name__ == "__main__":
    save_template(get_data())
