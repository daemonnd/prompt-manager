from prompt_manager.models import MetadataModel, PromptTemplateModel
from pathlib import Path
import toml
from prompt_manager.constants import PROMPT_TEMPLATES, PROMPTS_DIR


class CreateTemplate:
    def get_data(self) -> PromptTemplateModel:
        """
        Function that returns the metadata of the template as
        template data model and the template prompt as str
        """
        name = input("How should the new prompt template be called? ")
        description = input(
            f"How would you describe the new prompt template '{name}'? "
        )
        tags = input(
            f"Which tags should the new prompt template '{name}' get? Format: 'summary,transcript,video' "
        )
        prompt_file_name = f"{name}.md"
        prompt = input("Enter the prompt template, use '{}' for variables: ")
        return PromptTemplateModel(
            name=name,
            description=description,
            tags=tags,
            prompt_file_name=prompt_file_name,
            prompt=prompt,
        )

    def save_prompt(self, prompt: str, prompt_file_name: str | Path):
        """
        Method to save the prompt template itselft to a file
        """
        prompt_path: Path = PROMPTS_DIR / prompt_file_name
        try:
            with open(prompt_path, "w") as f:
                f.write(prompt)
        except IsADirectoryError:
            raise
        except FileNotFoundError:
            raise
        except PermissionError:
            raise
