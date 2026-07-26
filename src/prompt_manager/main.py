from argparse import ArgumentParser

from prompt_manager.features.create import CreateTemplate
from prompt_manager.features.render import render_template
from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.models import MetadataModel


def handle_add(args):
    creator = CreateTemplate()
    template_repo = PromptTemplateRepository()
    # ask the user for input
    data = creator.get_data()
    # save the raw prompt to a file
    creator.save_prompt(prompt=data.prompt, prompt_file_name=data.prompt_file_name)
    # add a db entry containing the metadata of the template
    template_repo.create_new(data=MetadataModel.from_template(data))


def handle_list(args):
    template_repo = PromptTemplateRepository()
    templates = template_repo.list_templates(args.fields)
    for template in templates:
        print(template)


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
    list_parser.add_argument(
        "--fields",
        help="Which fields should be displayed. Availible options: name, description, tags, prompt_file_name. More than one field can be selected. Default: name",
        nargs="+",
        choices=["name", "description", "tags", "prompt_file_name"],
        default=["name"],
    )
    list_parser.set_defaults(func=handle_list)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
