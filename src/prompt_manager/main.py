from argparse import ArgumentParser

from prompt_manager.features.create import CreateTemplate
from prompt_manager.features.render import render_template


def handle_add(args):
    creator = CreateTemplate()
    creator.create()


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

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
