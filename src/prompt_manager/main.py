import json
import logging
from argparse import ArgumentParser

import argcomplete

from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.errors import TemplateDBError
from prompt_manager.features.create import CreateTemplate
from prompt_manager.features.errors import TemplateCreationError
from prompt_manager.features.render import render_template
from prompt_manager.models import MetadataModel

logger = logging.getLogger(__name__)


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
            print(entry["name"])


def handle_render(args):
    render_template(args.template)


def main():
    parser = ArgumentParser(
        prog="prompt-manager",
        description="A basic prompt manager that lets you manage prompt templates",
    )
    subparsers = parser.add_subparsers()
    add_parser = subparsers.add_parser("add", help="add a new prompt template")
    add_parser.set_defaults(func=handle_add)

    render_parser = subparsers.add_parser(
        "render", help="render a prompt with filled in variables"
    )
    render_parser.add_argument("template")
    render_parser.set_defaults(func=handle_render)

    list_parser = subparsers.add_parser("list", help="list availible prompt templates")
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

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
