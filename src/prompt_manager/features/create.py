from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.errors import PromptFileWritingError
from prompt_manager.inputs.prompts import (
    get_description_session,
    get_prompt_session,
    get_tags_session,
    get_template_session,
)
from prompt_manager.models import PromptTemplateModel
from pathlib import Path
from prompt_manager.paths import PROMPTS_DIR


class CreateTemplate:
    def get_data(self) -> PromptTemplateModel:
        """
        Function that returns the metadata of the template as
        template data model and the template prompt as str
        """
        with PromptTemplateRepository() as template_db:
            names = template_db.list_templates(["name"])
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
            prompt = get_prompt_session().prompt(
                "Enter the prompt template, use '{}' for variables: \n"
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
                f"Could not open '{prompt_path}', because it is a dirctory: {str(e)}"
            ) from e
        except PermissionError as e:
            raise PromptFileWritingError(
                f"Could not write to '{prompt_path}', because of a permission error: {str(e)}"
            ) from e
