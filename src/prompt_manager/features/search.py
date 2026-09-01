import re

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import (
    BufferControl,
    FormattedTextControl,
)
from prompt_toolkit.styles import Style
from rapidfuzz import fuzz

from prompt_manager.db_repo import PromptTemplateRepository
from prompt_manager.features.errors import SearchInterrupted
from prompt_manager.features.load import load_prompt
from prompt_manager.models import PromptTemplateModel

SEARCH_INTERRUPTED = object()


class TemplateSearch:
    """
    Class for searching interactively for prompt templates.
    It will only suggest results that have the tag `tag`. If it is None, it searches through all templates.
    """

    def __init__(self, tags: str | None = None):
        self.templates: list[PromptTemplateModel] = []
        self.tags = tags
        repo = PromptTemplateRepository()
        metadatas = repo.get_all()
        for entry in metadatas:
            self.templates.append(
                PromptTemplateModel(
                    name=entry.name,
                    description=entry.description,
                    tags=str(entry.tags).split(
                        ","
                    ),  # it comes from the db, has to be a string
                    prompt_file_name=entry.prompt_file_name,
                    prompt=load_prompt(entry.prompt_file_name),
                )
            )
        self.reset()

    def reset(self):
        self.results = []
        self.selected_index = 0

    def search_templates(
        self,
        query: str,
        limit: int = 10,
    ) -> list:
        query = query.strip()

        if not query:
            return []

        results = []

        for template in self.templates:
            if self.tags is not None and not all(
                tag in template.tags for tag in self.tags
            ):
                continue
            name_score = fuzz.token_sort_ratio(
                query,
                template.name or "",
            )

            description_score = fuzz.token_sort_ratio(
                query,
                template.description or "",
            )

            tags = " ".join(template.tags) if template.tags else ""

            tags_score = fuzz.token_sort_ratio(
                query,
                tags,
            )

            filename_score = fuzz.token_sort_ratio(
                query,
                template.prompt_file_name or "",
            )

            prompt_score = fuzz.partial_token_sort_ratio(
                query,
                template.prompt or "",
            )

            score = (
                name_score * 0.45
                + tags_score * 0.30
                + description_score * 0.20
                + filename_score * 0.05
            )

            if score < 25:
                continue

            results.append(
                (
                    template,
                    score,
                    {
                        "name": name_score,
                        "tags": tags_score,
                        "description": description_score,
                        "filename": filename_score,
                        "prompt": prompt_score,
                    },
                )
            )

        results.sort(
            key=lambda result: result[1],
            reverse=True,
        )

        return results[:limit]

    @staticmethod
    def _prompt_context(query: str, prompt: str):
        if not query or not prompt:
            return None

        alignment = fuzz.partial_ratio_alignment(
            query,
            prompt,
            score_cutoff=60,
        )

        if alignment is None:
            return None

        start = alignment.dest_start
        end = alignment.dest_end

        words = list(re.finditer(r"\S+", prompt))

        if not words:
            return None

        start_word = None

        for index, match in enumerate(words):
            if match.start() <= start < match.end():
                start_word = index
                break

        end_word = None

        for index, match in enumerate(words):
            if match.start() < end <= match.end():
                end_word = index
                break

        if start_word is None or end_word is None:
            return None

        context_start_word = max(
            0,
            start_word - 3,
        )

        context_end_word = min(
            len(words) - 1,
            end_word + 3,
        )

        context_start = words[context_start_word].start()
        context_end = words[context_end_word].end()

        prefix = prompt[context_start:start]
        match = prompt[start:end]
        suffix = prompt[end:context_end]

        return (
            prefix,
            match,
            suffix,
            context_start > 0,
            context_end < len(prompt),
        )

    def _format_results(
        self,
        results,
        query: str,
    ):
        if not results:
            return "No matching templates."

        fragments = []

        for index, (template, score, field_scores) in enumerate(
            results,
        ):
            is_selected = index == self.selected_index

            if is_selected:
                number_style = "class:selected-number"
                name_style = "class:selected-name"
            else:
                number_style = "class:result-number"
                name_style = "class:name"

            fragments.append(
                (
                    number_style,
                    f"{index + 1}. ",
                )
            )

            fragments.append(
                (
                    name_style,
                    template.name,
                )
            )

            fragments.append(
                (
                    "class:score",
                    f"  {score:.0f}",
                )
            )

            fragments.append(("", "\n"))

            if template.description:
                fragments.append(
                    (
                        "class:description",
                        f"   Description: {template.description}",
                    )
                )
                fragments.append(("", "\n"))

            if template.tags:
                tags = ", ".join(tag.strip() for tag in template.tags if tag.strip())

                if tags:
                    fragments.append(
                        (
                            "class:tags",
                            f"   Tags: {tags}",
                        )
                    )
                    fragments.append(("", "\n"))

            prompt_score = field_scores["prompt"]

            if prompt_score >= 60 and template.prompt:
                context = self._prompt_context(
                    query,
                    template.prompt,
                )

                if context:
                    (
                        prefix,
                        match,
                        suffix,
                        has_prefix,
                        has_suffix,
                    ) = context

                    fragments.append(
                        (
                            "class:prompt-label",
                            "   Prompt: ",
                        )
                    )

                    if has_prefix:
                        fragments.append(
                            (
                                "class:prompt",
                                "...",
                            )
                        )

                    fragments.append(
                        (
                            "class:prompt",
                            prefix,
                        )
                    )

                    fragments.append(
                        (
                            "class:match",
                            match,
                        )
                    )

                    fragments.append(
                        (
                            "class:prompt",
                            suffix,
                        )
                    )

                    if has_suffix:
                        fragments.append(
                            (
                                "class:prompt",
                                "...",
                            )
                        )

                    fragments.append(("", "\n"))

            if template.prompt_file_name:
                fragments.append(
                    (
                        "class:filename",
                        f"   File: {template.prompt_file_name}",
                    )
                )
                fragments.append(("", "\n"))

            fragments.append(("", "\n"))

        return fragments

    def _update_results(
        self,
        results_control,
        query: str,
    ):
        self.results = self.search_templates(query)

        if self.results:
            self.selected_index = min(
                self.selected_index,
                len(self.results) - 1,
            )
        else:
            self.selected_index = 0

        results_control.text = self._format_results(
            self.results,
            query,
        )

        get_app().invalidate()

    def run(self) -> PromptTemplateModel | None:
        """
        Method to run the search engine.
        """
        results_control = FormattedTextControl("Type to search...")

        def on_search_changed(buffer):
            self.selected_index = 0

            self._update_results(
                results_control,
                buffer.text,
            )

        search_buffer = Buffer(
            name="search",
            multiline=False,
            on_text_changed=on_search_changed,
        )

        key_bindings = KeyBindings()

        @key_bindings.add("down")
        def _(event):
            if not self.results:
                return

            if self.selected_index < len(self.results) - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0

            results_control.text = self._format_results(
                self.results,
                search_buffer.text,
            )

            event.app.invalidate()

        @key_bindings.add("up")
        def _(event):
            if not self.results:
                return

            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = len(self.results) - 1

            results_control.text = self._format_results(
                self.results,
                search_buffer.text,
            )

            event.app.invalidate()

        @key_bindings.add("c-j")
        def _(event):
            if not self.results:
                return

            if self.selected_index < len(self.results) - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0

            results_control.text = self._format_results(
                self.results,
                search_buffer.text,
            )

            event.app.invalidate()

        @key_bindings.add("c-k")
        def _(event):
            if not self.results:
                return

            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = len(self.results) - 1

            results_control.text = self._format_results(
                self.results,
                search_buffer.text,
            )

            event.app.invalidate()

        @key_bindings.add("enter")
        def _(event):
            if not self.results:
                event.app.exit(None)
                return

            template = self.results[self.selected_index][0]
            event.app.exit(template)

        @key_bindings.add("escape")
        def _(event):
            event.app.exit(None)

        @key_bindings.add("c-c")
        def _(event):
            event.app.exit(SEARCH_INTERRUPTED)

        root = HSplit(
            [
                Window(
                    content=BufferControl(
                        buffer=search_buffer,
                    ),
                    height=1,
                ),
                Window(
                    content=results_control,
                ),
            ]
        )

        style = Style.from_dict(
            {
                "result-number": "fg:ansicyan",
                "name": "bold",
                "score": "fg:ansiblue",
                "description": "",
                "tags": "fg:ansimagenta",
                "filename": "fg:ansiyellow",
                "prompt-label": "bold",
                "prompt": "",
                "match": "bold",
                "selected-number": "bold fg:ansicyan",
                "selected-name": "bold reverse",
            }
        )

        application = Application(
            layout=Layout(root),
            key_bindings=key_bindings,
            style=style,
            full_screen=True,
        )

        self.reset()
        result = application.run()
        if result is SEARCH_INTERRUPTED:
            raise SearchInterrupted()
        return result
