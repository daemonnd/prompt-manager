from prompt_toolkit.completion import Completer, Completion


class TagCompleter(Completer):
    """
    Autocompletes comma-separated tags.

    Example:
        ai,summ<TAB>

    becomes

        ai,summary
    """

    def __init__(self, tags_list: list[str]) -> None:
        self._tags = sorted(tags_list)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        current_tag = text.split(",")[-1].strip()

        for tag in self._tags:
            if tag.startswith(current_tag):
                yield Completion(
                    tag,
                    start_position=-len(current_tag),
                )


class PlaceholderCompleter(Completer):
    """
    Autocompletes placeholders inside prompt templates.

    Example:
        {inp<TAB>

    becomes

        {input_text}
    """

    def __init__(self, placeholders: list[str]) -> None:
        self._placeholders = sorted(set(placeholders))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        start = text.rfind("{")
        end = text.rfind("}")

        # Cursor is not currently inside a placeholder.
        if start == -1 or start < end:
            return

        current = text[start + 1 :]

        for placeholder in self._placeholders:
            if placeholder.startswith(current):
                yield Completion(
                    placeholder + "}",
                    start_position=-len(current),
                )
