from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

from prompt_manager.inputs.validators import (
    validate_length,
    validate_placeholders,
    validate_tags,
    validate_template_name,
)


class TemplateNameValidator(Validator):
    """
    Validates a prompt template name.

    Rules:
    - only lowercase letters
    - digits
    - '_' and '-'
    - cannot start/end with '_' or '-'
    """

    def __init__(self, existing_names: list[str]) -> None:
        super().__init__()
        self.existing_names: list[str] = existing_names

    def validate(self, document: Document) -> None:
        text = document.text.strip()

        failure = validate_template_name(
            name=text,
            existing_names=self.existing_names,
        )

        if failure is not None:
            raise ValidationError(
                message=failure.message,
                cursor_position=failure.cursor_position,
            )


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

        failure = validate_placeholders(prompt=text)

        if failure is not None:
            raise ValidationError(
                message=failure.message,
                cursor_position=failure.cursor_position,
            )


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
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length
        self.strip = strip

    def validate(self, document: Document) -> None:
        text = document.text

        failure = validate_length(
            text=text,
            min_length=self.min_length,
            max_length=self.max_length,
            strip=self.strip,
        )

        if failure is not None:
            raise ValidationError(
                message=failure.message,
                cursor_position=failure.cursor_position,
            )


class TagValidator(Validator):
    """
    Validates a comma-separated tag list.

    Example:
        summary,ai,python
    """

    def validate(self, document: Document) -> None:
        text = document.text

        failure = validate_tags(tag_text=text)

        if failure is not None:
            raise ValidationError(
                message=failure.message,
                cursor_position=failure.cursor_position,
            )
