import string
from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.load import load_prompt, load_template
import pyperclip

template_repo = PromptTemplateRepository()


def render_template(name: str):
    template = template_repo.get(name)
    if template is None:
        print(f"No prompt template with name '{name}' found in the database.")
        return
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
    print(final_prompt)
