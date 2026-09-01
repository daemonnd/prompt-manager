import json
import logging
import sys
from argparse import ArgumentParser

import argcomplete
from rich import print as rprint

from prompt_manager.config.loader import load_config
from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.errors import TemplateDBError
from prompt_manager.features.create import CreateTemplate
from prompt_manager.features.errors import SearchInterrupted, TemplateCreationError
from prompt_manager.features.remove import remove_template
from prompt_manager.features.render import render_template
from prompt_manager.features.search import TemplateSearch
from prompt_manager.features.show import show_prompt
from prompt_manager.models import MetadataModel

logger = logging.getLogger(__name__)


def _clear_terminal():
    print("\033[2J\033[H", end="")


def autocomplete_template_names(prefix: str, parsed_args, **kwargs):
    template_repo = PromptTemplateRepository()
    return list(template_repo.get_template_name_by_prefix(prefix=prefix))


def handle_list(args, config):
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


def handle_render(args, config):
    render_template(args.template)


def autocomplete_tags(prefix: str, parsed_args, **kwargs):
    matching_tags = []
    with PromptTemplateRepository() as repo:
        tags = repo.get_all_tags()
        for tag in tags:
            if tag.startswith(prefix):
                #            yield tag
                matching_tags.append(tag)
    return matching_tags


def handle_search(args, config):
    searcher = TemplateSearch()
    result = searcher.run()
    if result is not None:
        render_template(result.name)


def handle_run(args, config):
    searcher = TemplateSearch(args.tags)
    while True:
        result = searcher.run()
        _clear_terminal()
        if result is None:
            rprint("[red]No matching templates found to render.[/red]")
            input("Press <ENTER> to continue...")
        else:
            rprint(f"Rendering Template: [bold][cyan]{result.name}[/cyan][/bold]")
            try:
                render_template(result.name)
            except KeyboardInterrupt:
                continue
            input("Press <ENTER> to continue...")


def handle_remove(args, config):
    for template in args.template_name:
        remove_template(template)


def handle_show(args, config):
    show_prompt(args.template_name)


def validate_add_args(args, parser):
    core_args = (
        args.name is not None,
        args.tags is not None,
        args.prompt_file is not None,
    )

    provided_core_args = sum(core_args)

    if provided_core_args == 0 and args.description is None:
        return

    if provided_core_args == 3:
        return

    parser.error(
        "--name, --tags, and --prompt-file are required when using "
        "non-interactive mode; --description is optional"
    )


def handle_add(args, config):
    validate_add_args(args, args.parser)

    creator = CreateTemplate(config=config)
    template_repo = PromptTemplateRepository()

    if args.name is not None:
        # non-interactive creation
        data = creator.create_from_args(
            name=args.name,
            description=args.description,
            tags=args.tags,
            prompt_file=args.prompt_file,
        )
    else:
        # interactive creation
        data = creator.get_data()

    try:
        creator.save_prompt(
            prompt=data.prompt,
            prompt_file_name=data.prompt_file_name,
        )
        template_repo.create_new(data=MetadataModel.from_template(data))
    except TemplateCreationError as e:
        logger.error(
            f"Failed to save the prompt for prompt template '{data.name}': {e!s}"
        )
    except TemplateDBError as e:
        logger.error(
            f"Failed to write template '{data.name}' metadata to database: {e!s}"
        )


def main():
    parser = ArgumentParser(
        prog="prompt-manager",
        description="A basic prompt manager that lets you manage prompt templates",
    )
    subparsers = parser.add_subparsers(
        required=True,
    )
    add_parser = subparsers.add_parser(
        "add",
        help="add a new prompt template. If one flag is used, the other ones (except description) are required because the prompt template will be created non-interactively",
    )
    add_parser.add_argument(
        "--name", help="The title of the prompt template to be created"
    )
    add_parser.add_argument(
        "--description",
        help="The description of the prompt template to be created. Optional. ",
    )
    add_parser.add_argument(
        "--tags",
        nargs="+",
        help="The tags of the prompt template to be created. Usage: --tags summary summarization",
    )
    add_parser.add_argument(
        "--prompt-file",
        help="The path to a plaintext prompt file. The entire contents of that file are used as prompt. ",
    )
    add_parser.set_defaults(
        func=handle_add,
        parser=add_parser,
    )

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
    ).completer = autocomplete_tags
    search_parser.set_defaults(func=handle_search)

    run_parser = subparsers.add_parser(
        "run", help="Run the search and render the selected result infinitely"
    )
    run_parser.add_argument(
        "--tags",
        help="Only select the templates that include the tag for search and rendering",
        nargs="+",
        default=None,
    ).completer = autocomplete_tags

    run_parser.set_defaults(func=handle_run)
    remove_parser = subparsers.add_parser(
        "rm", help="Remove the selected prompt template(s)"
    )
    remove_parser.add_argument(
        "template_name", nargs="+"
    ).completer = autocomplete_template_names
    remove_parser.set_defaults(func=handle_remove)

    show_parser = subparsers.add_parser("show", help="Show a prompt template")
    show_parser.add_argument(
        "template_name", help="The name of the template you want to show"
    ).completer = autocomplete_template_names
    show_parser.set_defaults(func=handle_show)

    config = load_config()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args, config)
        except KeyboardInterrupt, SearchInterrupted:
            rprint("[red]Exiting due to KeyboardInterrupt[/red]")
            sys.exit(130)


if __name__ == "__main__":
    main()
