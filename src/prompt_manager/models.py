from pydantic import BaseModel


class MetadataModel(BaseModel):
    name: str
    description: str | None
    tags: list[str] | str
    prompt_file_name: str

    @classmethod
    def from_template(cls, template: PromptTemplateModel):
        return MetadataModel(
            name=template.name,
            description=template.description,
            tags=template.tags,
            prompt_file_name=template.prompt_file_name,
        )


class PromptTemplateModel(MetadataModel):
    name: str
    prompt: str
