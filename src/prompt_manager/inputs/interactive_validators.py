import re
import string

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

from prompt_manager.inputs.validators import validate_template_name


class TemplateNameValidator(Validator):
    """
    Validates a prompt template name.
    It can also validate tags by using tags=True which allows commas

    Rules:
    - only lowercase letters
    - digits
    - '_' and '-'
    - cannot start/end with '_' or '-' or ','
    """

    def __init__(self, existing_names: list[str]) -> None:
        super().__init__()
        self.existing_names: list[str] = existing_names

    def validate(self, document: Document) -> None:
        text = document.text.strip()


class PlaceholderValidator(Validator):
    """
    Validates a prompt template.

    Rules:
    - matching braces
    - every placeholder is snake_case
    - no empty {}
    """

    def validate(self, document: Document) -> None:
        text = document.text


class LengthValidator(Validator):
    """
    Validates the length of the input.

    Parameters
    ----------
    min_length:
        Minimum number of characters.
    max_length:
        Maximum number of characters.
    strip:
        Whether leading/trailing whitespace should be ignored.
    """

    def __init__(
        self,
        *,
        min_length: int = 0,
        max_length: int | None = None,
        strip: bool = True,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.strip = strip

    def validate(self, document: Document) -> None:
        text = document.text


class TagValidator(Validator):
    """
    Validates a comma-separated tag list.

    Example:
        summary,ai,python
    """

    def validate(self, document: Document) -> None:
        text = document.text
