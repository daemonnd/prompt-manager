import logging

from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.errors import TemplateDBError
from prompt_manager.paths import PROMPTS_DIR

logger = logging.getLogger(__name__)


def remove_template(name: str):
    with PromptTemplateRepository() as repo:
        try:
            template = repo.get(name)
        except TemplateDBError as e:
            logger.exception(
                f"Failed to gather information about themplate '{name}' that is about to get removed: {e!s}"
            )
        try:
            repo.remove_template(name)
        except TemplateDBError as e:
            logger.exception(f"Failed to remove template '{name}': {e!s}")

    (PROMPTS_DIR / template.prompt_file_name).unlink()
