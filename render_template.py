from platformdirs import user_data_dir
from pathlib import Path
import string
from load_template import load_template, load_prompt

prompt_file: Path = (
    Path(user_data_dir("prompt_library")) / "prompts" / "summary_prompt.md"
)
with open(prompt_file) as f:
    prompt = f.read()

formatter = string.Formatter()

placeholders: list[str] = []

for literal_text, field_name, format_spec, conversion in formatter.parse(prompt):
    if field_name is not None:
        placeholders.append(field_name)

values = {}
for placeholder in placeholders:
    values[placeholder] = input(f"What is the {placeholder} of the prompt: ")
