from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.errors import TemplateNotFoundError
from prompt_manager.features.load import load_prompt
from prompt_manager.models import PromptTemplateModel

from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.console import Console

console = Console()


def show_prompt(name: str) -> None:
    with PromptTemplateRepository() as repo:
        metadata = repo.get(name)
        if metadata is None:
            raise TemplateNotFoundError(
                f"The template '{name}' was not found and can therefore not be shown."
            )
        prompt = load_prompt(prompt_file_name=metadata.prompt_file_name)

        template = PromptTemplateModel.from_data(metadata=metadata, prompt=prompt)
        _print_template(template)


def _print_template(template: PromptTemplateModel):
    console.print()

    tags = (
        ", ".join(template.tags) if isinstance(template.tags, list) else template.tags
    )

    metadata = Table.grid(padding=(0, 1))
    metadata.add_column(style="bold cyan", no_wrap=True)
    metadata.add_column()

    metadata.add_row("Name", template.name)
    metadata.add_row("Description", template.description)
    metadata.add_row("Tags", tags)

    console.print(metadata)
    console.print()

    prompt = Text(template.prompt)

    console.print(
        Panel(
            prompt,
            title="[bold magenta]Prompt[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    console.print()
