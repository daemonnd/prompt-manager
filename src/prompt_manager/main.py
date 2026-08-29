from rich import print as rprint
import logging
import json
import logging
from argparse import ArgumentParser

import argcomplete

from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.errors import TemplateDBError
from prompt_manager.features.create import CreateTemplate
from prompt_manager.features.errors import TemplateCreationError
from prompt_manager.features.remove import remove_template
from prompt_manager.features.render import render_template
from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.search import TemplateSearch
from prompt_manager.features.show import show_prompt
from prompt_manager.models import MetadataModel

logger = logging.getLogger(__name__)


def _clear_terminal():
    print("\033[2J\033[H", end="")


def handle_add(args):
    creator = CreateTemplate()
    template_repo = PromptTemplateRepository()
    # ask the user for input
    data = creator.get_data()
    # save the raw prompt to a file
    try:
        creator.save_prompt(prompt=data.prompt, prompt_file_name=data.prompt_file_name)
        # add a db entry containing the metadata of the template
        template_repo.create_new(data=MetadataModel.from_template(data))
    except TemplateCreationError as e:
        logger.error(
            f"Failed to save the prompt for prompt template '{data.name}': {str(e)}"
        )
    except TemplateDBError as e:
        logger.error(
            f"Failed to write template '{data.name}' metadata to database: {str(e)}"
        )


def handle_list(args):
    template_repo = PromptTemplateRepository()
    if args.all:
        entries = template_repo.get_all()
        for entry in entries:
            print(json.dumps(entry.__dict__))
    elif args.fields:
        entries = template_repo.list_templates(args.fields)
        for entry in entries:
            print(json.dumps(entry))
    else:
        entries = template_repo.list_templates(["name"])
        for entry in entries:
            rprint(entry["name"])


def handle_render(args):
    render_template(args.template)


def autocomplete_template_names(prefix: str, parsed_args, **kwargs):
    template_repo = PromptTemplateRepository()
    return list(template_repo.get_template_name_by_prefix(prefix=prefix))


# TODO: add autcomplete func for tags


def handle_search(args):
    searcher = TemplateSearch(args.tags)
    result = searcher.run()
    if result is not None:
        render_template(result.name)


def handle_run(args):
    searcher = TemplateSearch(args.tags)
    while True:
        result = searcher.run()
        _clear_terminal()
        if result is None:
            rprint("[red]No matching templates found to render.[/red]")
            input("Press <ENTER> to continue...")
        else:
            rprint(f"Rendering Template: [bold][cyan]{result.name}[/cyan][/bold]")
            render_template(result.name)
            input("Press <ENTER> to continue...")


def handle_remove(args):
    remove_template(args.template_name)


def handle_show(args):
    show_prompt(args.template_name)


def main():
    parser = ArgumentParser(
        prog="prompt-manager",
        description="A basic prompt manager that lets you manage prompt templates",
    )
    subparsers = parser.add_subparsers(
        required=True,
    )
    add_parser = subparsers.add_parser("add", help="add a new prompt template")
    add_parser.set_defaults(func=handle_add)

    render_parser = subparsers.add_parser(
        "render", help="render a prompt with filled in variables"
    )
    render_parser.add_argument("template").completer = autocomplete_template_names
    render_parser.set_defaults(func=handle_render)

    list_parser = subparsers.add_parser("ls", help="list availible prompt templates")
    list_fields_exlcusives = list_parser.add_mutually_exclusive_group(required=False)
    list_fields_exlcusives.add_argument(
        "--fields",
        help="""Which fields should be displayed. 
            Availible options: name, description, tags, prompt_file_name. More than one field can be selected. 
            Output format: jsonl""",
        nargs="+",
        choices=["name", "description", "tags", "prompt_file_name"],
    )
    list_fields_exlcusives.add_argument(
        "--all",
        help="Display each field. Equivalent to '--fields name description tags prompt_file_name'",
        action="store_true",
    )
    list_parser.set_defaults(func=handle_list)

    search_parser = subparsers.add_parser(
        "search", help="search for prompt templates matching the search criteria"
    )
    search_parser.add_argument(
        "--tags",
        help="Only select the templates that include the tag for search and rendering",
        nargs="+",
        default=None,
    )
    search_parser.set_defaults(func=handle_search)

    run_parser = subparsers.add_parser(
        "run", help="Run the search and render the selected result infinitely"
    )
    run_parser.add_argument(
        "--tags",
        help="Only select the templates that include the tag for search and rendering",
        nargs="+",
        default=None,
    )
    run_parser.set_defaults(func=handle_run)

    remove_parser = subparsers.add_parser(
        "rm", help="Remove the selected prompt template"
    )
    remove_parser.add_argument("template_name").completer = autocomplete_template_names
    remove_parser.set_defaults(func=handle_remove)

    show_parser = subparsers.add_parser("show", help="Show a prompt template")
    show_parser.add_argument(
        "template_name", help="The name of the template you want to show"
    ).completer = autocomplete_template_names
    show_parser.set_defaults(func=handle_show)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
