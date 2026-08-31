class TemplateDBError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InternalDBError(TemplateDBError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DBIntegrityError(TemplateDBError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DBOperationalError(TemplateDBError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DBDataValidationError(TemplateDBError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidAddArgumentsError(Exception):
    pass
