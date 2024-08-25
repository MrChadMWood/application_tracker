from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum

'''
Todo- refactor the fields, which can inherit from a base field class. 
The Foreign-Key fields have different attributes than any other, and shouldn't
cloud the namespace of other field types. This will allow for better control over behavior
based on field type.
'''

class FieldType(str, Enum):
    model_config = ConfigDict(extra="forbid")

    NUMBER = 'number'
    DATE = 'date'
    TEXT = 'text'
    MULTILINE_TEXT = 'multiline-text'
    BOOLEAN = 'boolean'
    FOREIGN_KEY = 'foreign-key'

    def __repr__(self):
        return self.name

class Field(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FieldType | str
    form_name: str
    form_endpoint: str
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
