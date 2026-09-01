from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings

from prompt_manager.inputs.completers import PlaceholderCompleter, TagCompleter
from prompt_manager.inputs.validators import (
    LengthValidator,
    PlaceholderValidator,
    TagValidator,
    TemplateNameValidator,
)

bindings = KeyBindings()


@bindings.add("c-d")
def _(event):
    """
    Finish multiline input with Ctrl+D.
    """
    event.app.exit(result=event.app.current_buffer.text)


def get_template_session(existing_names: list[str]):
    return PromptSession(
        validator=TemplateNameValidator(existing_names),
        auto_suggest=AutoSuggestFromHistory(),
        history=InMemoryHistory(),
        key_bindings=bindings,
    )


def get_prompt_session():
    return PromptSession(
        multiline=True,
        validator=PlaceholderValidator(),
        completer=FuzzyCompleter(
            PlaceholderCompleter(
                [
                    "input_text",
                    "goal_of_summary",
                    "target_audience",
                    "style",
                    "length_constraint",
                    "key_focus_areas",
                ]
            )
        ),
        complete_while_typing=True,
        auto_suggest=AutoSuggestFromHistory(),
        history=InMemoryHistory(),
        key_bindings=bindings,
        editing_mode=EditingMode.VI,
    )


def get_description_session():
    return PromptSession(
        validator=LengthValidator(max_length=100, strip=True),
        auto_suggest=AutoSuggestFromHistory(),
        history=InMemoryHistory(),
    )


def get_tags_session(tags_list: list[str]):
    return PromptSession(
        validator=TagValidator(),
        completer=FuzzyCompleter(TagCompleter(tags_list)),
        complete_while_typing=True,
        auto_suggest=AutoSuggestFromHistory(),
        history=InMemoryHistory(),
    )


def get_search_prompt():
    return PromptSession(
        validator=LengthValidator(min_length=1),
    )
