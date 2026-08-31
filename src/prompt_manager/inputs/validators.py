import re
from dataclasses import dataclass
import string

_TEMPLATE_NAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")


@dataclass
class ValidationFailure:
    message: str
    cursor_position: int


def validate_template_name(
    name: str, existing_names: list[str]
) -> ValidationFailure | None:
    if not name:
        return ValidationFailure(
            message="Template name cannot be empty.",
            cursor_position=0,
        )

    if not _TEMPLATE_NAME_PATTERN.fullmatch(name):
        return ValidationFailure(
            message="Only a-z, 0-9, '_' and '-' are allowed.",
            cursor_position=len(name),
        )

    if name[0] in "_-":
        return ValidationFailure(
            message="Template name cannot start with '_' or '-'.",
            cursor_position=0,
        )

    if name[-1] in "_-,":
        return ValidationFailure(
            message="Template name cannot end with '_' or '-'.",
            cursor_position=len(name),
        )

    if name in existing_names:
        return ValidationFailure(
            message=f"Template name '{name}' has already been used",
            cursor_position=len(name),
        )


_PLACEHOLDER_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_placeholders(prompt: str):
    try:
        formatter = string.Formatter()

        for _, field_name, _, _ in formatter.parse(prompt):
            if field_name is None:
                continue

            if field_name == "":
                return ValidationFailure(
                    message="Empty placeholders '{}' are not allowed.",
                    cursor_position=prompt.find("{}"),
                )

            if not _PLACEHOLDER_PATTERN.fullmatch(field_name):
                position = prompt.find("{" + field_name)

                return ValidationFailure(
                    message=(
                        f"'{field_name}' is not a valid placeholder. Use snake_case."
                    ),
                    cursor_position=max(position, 0),
                )

    except ValueError as e:
        return ValidationFailure(message=str(e), cursor_position=0)


def validate_length(
    text: str,
    min_length: int = 0,
    max_length: int | None = None,
    strip: bool = True,
):
    if strip:
        text = text.strip()

    length = len(text)

    if length < min_length:
        return ValidationFailure(
            message=f"Must contain at least {min_length} characters, contains {length}",
            cursor_position=len(text),
        )

    if max_length is not None and length > max_length:
        return ValidationFailure(
            message=f"Must contain at most {max_length} characters, contains {length}",
            cursor_position=len(text),
        )


_TAG_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def validate_tags(tag_text: str):
    if not tag_text:
        return ValidationFailure(
            message="At least one tag is required.",
            cursor_position=0,
        )

    tags = [tag for tag in tag_text.split(",")]
    for tag in tags:
        if not tag:
            return ValidationFailure(
                message="Empty tags are not allowed.",
                cursor_position=len(tag_text),
            )

        if " " in tag:
            return ValidationFailure(
                message=f"spaces are not allowed for tags, but '{tag}' contains at least one.",
                cursor_position=tag_text.find(tag),
            )
        if not _TAG_PATTERN.fullmatch(tag):
            return ValidationFailure(
                message=f"'{tag}' contains invalid characters. Only a-z, 0-9, '_' and '-' are allowed.",
                cursor_position=tag_text.find(tag),
            )

        if tag[0] in "_-":
            return ValidationFailure(
                message=f"'{tag}' cannot start with '_' or '-'.",
                cursor_position=tag_text.find(tag),
            )

        if tag[-1] in "_-":
            return ValidationFailure(
                message=f"'{tag}' cannot end with '_' or '-'.",
                cursor_position=tag_text.find(tag) + len(tag),
            )
        occurences = 0
        for t in tags:
            if t == tag:
                occurences += 1

        if occurences > 1:
            return ValidationFailure(
                message=f"'{tag}' is already used, duplicate tags are not allowed",
                cursor_position=tag_text.find(tag) + len(tag),
            )
