import re
import string

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator


_TEMPLATE_NAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")


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

        if not text:
            raise ValidationError(
                message="Template name cannot be empty.",
                cursor_position=0,
            )

        if not _TEMPLATE_NAME_PATTERN.fullmatch(text):
            raise ValidationError(
                message="Only a-z, 0-9, '_' and '-' are allowed.",
                cursor_position=len(document.text),
            )

        if text[0] in "_-":
            raise ValidationError(
                message="Template name cannot start with '_' or '-'.",
                cursor_position=0,
            )

        if text[-1] in "_-,":
            raise ValidationError(
                message="Template name cannot end with '_' or '-'.",
                cursor_position=len(document.text),
            )

        if text in self.existing_names:
            raise ValidationError(
                message=f"Template name '{text}' has already been used",
                cursor_position=len(document.text),
            )


_PLACEHOLDER_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class PlaceholderValidator(Validator):
    """
    Validates a prompt template.

    Rules:
    - matching braces
    - every placeholder is snake_case
    - no empty {}
    """

    def validate(self, document: Document) -> None:
        raise NoeImplementedError("Make escaping { possible and {{ is not allowed")
        text = document.text

        try:
            formatter = string.Formatter()

            for _, field_name, _, _ in formatter.parse(text):
                if field_name is None:
                    continue

                if field_name == "":
                    raise ValidationError(
                        message="Empty placeholders '{}' are not allowed.",
                        cursor_position=text.find("{}"),
                    )

                if not _PLACEHOLDER_PATTERN.fullmatch(field_name):
                    position = text.find("{" + field_name)

                    raise ValidationError(
                        message=(
                            f"'{field_name}' is not a valid placeholder. "
                            "Use snake_case."
                        ),
                        cursor_position=max(position, 0),
                    )

        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                cursor_position=len(text),
            ) from exc


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

        if self.strip:
            text = text.strip()

        length = len(text)

        if length < self.min_length:
            raise ValidationError(
                message=f"Must contain at least {self.min_length} characters, contains {length}",
                cursor_position=len(document.text),
            )

        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                message=f"Must contain at most {self.max_length} characters, contains {length}",
                cursor_position=len(document.text),
            )


_TAG_PATTERN = re.compile(r"^[a-z0-9_-]+$")


class TagValidator(Validator):
    """
    Validates a comma-separated tag list.

    Example:
        summary,ai,python
    """

    def validate(self, document: Document) -> None:
        text = document.text.strip()

        if not text:
            raise ValidationError(
                message="At least one tag is required.",
                cursor_position=0,
            )

        tags = [tag.strip() for tag in text.split(",")]

        for tag in tags:
            if not tag:
                raise ValidationError(
                    message="Empty tags are not allowed.",
                    cursor_position=len(document.text),
                )

            if not _TAG_PATTERN.fullmatch(tag):
                raise ValidationError(
                    message=f"'{tag}' contains invalid characters. Only a-z, 0-9, '_' and '-' are allowed.",
                    cursor_position=document.text.find(tag),
                )

            if tag[0] in "_-":
                raise ValidationError(
                    message=f"'{tag}' cannot start with '_' or '-'.",
                    cursor_position=document.text.find(tag),
                )

            if tag[-1] in "_-":
                raise ValidationError(
                    message=f"'{tag}' cannot end with '_' or '-'.",
                    cursor_position=document.text.find(tag) + len(tag),
                )
            occurences = 0
            for t in tags:
                if t == tag:
                    occurences += 1

            if occurences > 1:
                raise ValidationError(
                    message=f"'{tag}' is already used, duplicate tags are not allowed",
                    cursor_position=document.text.find(tag) + len(tag),
                )
