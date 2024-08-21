from pydantic import BaseModel, Field, model_validator
from enum import Enum


class FieldType(str, Enum):
    NUMBER = 'number'
    DATE = 'date'
    TEXT = 'text'
    MULTILINE_TEXT = 'multiline-text'
    BOOLEAN = 'boolean'
    FOREIGN_KEY = 'foreign-key'

    def __repr__(self):
        return self.name

class Field(BaseModel):
    name: str
    type: FieldType | str
    is_required: bool
    default: object = None
    parent_endpoint: str | None = None
    parent_id: str | None = None
    parent_label: str | None = None
    parent_allow_new: bool = False

    @model_validator(mode='before')
    def validate_foreign_key(cls, values):
        typ = values['type']
        if not isinstance(typ, FieldType):
            values['type'] = FieldType(typ)

        return values
