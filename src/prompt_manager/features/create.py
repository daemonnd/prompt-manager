import logging
from pathlib import Path

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError
from rich import print as rprint

from prompt_manager.config.models import AppConfig
from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.editor import EditorInput
from prompt_manager.features.errors import PromptFileWritingError, TemplateCreationError
from prompt_manager.inputs.prompts import (
    get_description_session,
    get_prompt_session,
    get_tags_session,
    get_template_session,
)
from prompt_manager.inputs.validators import PlaceholderValidator
from prompt_manager.models import PromptTemplateModel
from prompt_manager.paths import PROMPTS_DIR

logger = logging.getLogger(__name__)


class CreateTemplate:
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config

    def get_data(self) -> PromptTemplateModel:
        """
        Function that returns the metadata of the template as
        template data model and the template prompt as str
        """
        with PromptTemplateRepository() as template_db:
            names = template_db.list_templates(["name"])
            prompt: str | None = None
            existing_names: list[str] = []
            for entry in names:
                existing_names.append(entry["name"])
            name = get_template_session(existing_names).prompt(
                "How should the new prompt template be called? "
            )
            description: str | None = get_description_session().prompt(
                f"How would you describe the new prompt template '{name}'? (Optional, ENTER to skip) "
            )  # returns a string, at that point description is a string and not None
            if description.replace(" ", "") == "":
                description = None
            tags = get_tags_session(
                [
                    "summary",
                    "summarization",
                    "favourite",
                    "ai",
                    "transcript",
                    "video",
                    "coding",
                    "assistant",
                    "finances",
                    "work",
                    "school",
                    "fitness",
                    "sports",
                    "health",
                    "research",
                    "agent",
                    "traveling",
                    "technology",
                ]
            ).prompt(
                f"Which tags should the new prompt template '{name}' get? \nFormat: 'summary,transcript,video' "
            )
            prompt_file_name = f"{name}.md"
            if self.config.editor_inputs.prompt is False:
                prompt = get_prompt_session().prompt(
                    "Enter the prompt template, use '{}' for variables: \n"
                )
            else:
                rprint(
                    "[yellow]Your editor will open. \nEnter the prompt for the prompt template, use '{}' for placeholders.\nWhen done, save and exit.[/yellow]"
                )
                with EditorInput() as editor:
                    for i in range(5):
                        input(
                            f"Press <ENTER> to open the editor... (attempts remaining: {5 - i}) "
                        )
                        try:
                            prompt = editor.get_input()
                            PlaceholderValidator().validate(
                                document=Document(text=prompt)
                            )
                        except ValidationError as e:
                            logger.warning(
                                f"Failed to create a valid prompt because of the following error: {e!s}",
                                exc_info=True,
                            )
                        else:
                            break
                    else:
                        raise TemplateCreationError(
                            "Failed to get the prompt because of previous errors"
                        )

            if prompt is None:
                raise TemplateCreationError(
                    "Failed to create template because the prompt is missing"
                )

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
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        try:
            prompt_path.touch(exist_ok=True)
            with open(prompt_path, "w") as f:
                f.write(prompt)
        except IsADirectoryError as e:
            raise PromptFileWritingError(
                f"Could not open '{prompt_path}', because it is a dirctory: {e!s}"
            ) from e
        except PermissionError as e:
            raise PromptFileWritingError(
                f"Could not write to '{prompt_path}', because of a permission error: {e!s}"
            ) from e
