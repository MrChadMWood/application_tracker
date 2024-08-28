# ./src/schemas/py
from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


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

class FieldTemplate(BaseModel):
    """Used for templating fields prior to form initialization"""
    name: str
    type: FieldType | str
    is_required: bool
    default: object = None
    parent_endpoint: str | None = None

    @model_validator(mode='before')
    def check_foreign_key(cls, values):
        if values['type'] == FieldType.FOREIGN_KEY and not values.get('parent_endpoint'):
            raise ValueError("`parent_endpoint` must be provided when `type` is 'foreign-key'")
        return values

    def as_field(self, forms=None, **kwargs):
        """Convert FieldTemplate to a Field or ForeignKeyField"""
        field_kwargs = self.model_dump()
        if self.type == FieldType.FOREIGN_KEY:
            field_class = ForeignKeyField
            parent_form = forms[self.parent_endpoint]
            field_kwargs.update({
                'parent_id': parent_form.id_field,
                'parent_label': parent_form.label_field,
                'parent_allow_new': parent_form.allow_children_make_new,
            })
        else:
            field_class = Field
            field_kwargs.pop('parent_endpoint', None)  # Remove parent_endpoint for non-foreign-key fields

        logger.info(f'KWARGS Used: {kwargs}')
        return field_class(**field_kwargs, **kwargs)

class Field(BaseModel):
    """Used to represent basic fields within a form"""
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FieldType | str
    is_required: bool
    default: object = None
    form_name: str
    form_endpoint: str

    @model_validator(mode='before')
    def validate_foreign_key(cls, values):
        typ = values['type']
        if not isinstance(typ, FieldType):
            values['type'] = FieldType(typ)

        return values

class ForeignKeyField(Field):
    """Used to represent foreign-key fields within a form"""
    parent_endpoint: str | None = None
    parent_id: str | None = None
    parent_label: str | None = None
    parent_allow_new: bool = False
