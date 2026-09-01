import string

import pyperclip
from rich import print as rprint
from rich.console import Console

from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.errors import TemplateNotFoundError
from prompt_manager.features.load import load_prompt

console = Console()

template_repo = PromptTemplateRepository()


def render_template(name: str):
    template = template_repo.get(name)
    if template is None:
        raise TemplateNotFoundError(
            f"No prompt template with name '{name}' found in the database."
        )
    prompt: str = load_prompt(prompt_file_name=template.prompt_file_name)
    formatter = string.Formatter()

    placeholders: list[str] = []

    for literal_text, field_name, format_spec, conversion in formatter.parse(prompt):
        if field_name is not None:
            placeholders.append(field_name)

    values = {}
    for placeholder in placeholders:
        values[placeholder] = input(f"What is the {placeholder} of the prompt: ")

    final_prompt = prompt.format(**values)

    pyperclip.copy(final_prompt)

    width = console.width

    left_dashes = (width - len(name)) // 2
    right_dashes = width - len(name) - left_dashes

    rprint(f"[magenta]{'-' * left_dashes}{name}{'-' * right_dashes}[/magenta]")
    print(final_prompt)
    rprint(f"[magenta]{'-' * width}[/magenta]")
