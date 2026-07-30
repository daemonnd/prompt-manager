class RenderingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TemplateNotFoundError(RenderingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PromptFileReadingError(RenderingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TemplateCreationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PromptFileWritingError(TemplateCreationError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
