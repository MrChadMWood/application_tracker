# ./src/schemas.py
from pydantic import BaseModel, Field as PydanticField, ConfigDict, model_validator
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

class BaseField(BaseModel):
    """Base class for all form fields."""
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FieldType | str
    is_required: bool
    default: object = None

    @model_validator(mode='before')
    def ensure_field_type(cls, values):
        typ = values.get('type')
        if isinstance(typ, str) and not isinstance(typ, FieldType):
            try:
                values['type'] = FieldType(typ)
            except ValueError:
                raise ValueError(f"Invalid field type: {typ}")
        return values

class FieldTemplate(BaseField):
    """Template for initializing fields in forms."""
    parent_endpoint: str | None = None

    @model_validator(mode='before')
    def validate_foreign_key(cls, values):
        if values['type'] == FieldType.FOREIGN_KEY and not values.get('parent_endpoint'):
            raise ValueError("`parent_endpoint` must be provided when `type` is 'foreign-key'")
        return values

    def as_field(self, forms=None, **kwargs):
        """Convert FieldTemplate to a specific Field instance."""
        if self.type == FieldType.FOREIGN_KEY:
            return self._create_foreign_key_field(forms, **kwargs)
        else:
            return self._create_standard_field(**kwargs)

    def _create_standard_field(self, **kwargs):
        """Creates a standard Field instance."""
        field_data = self._prepare_field_data()
        field_data.pop('parent_endpoint', None)
        return Field(**field_data, **kwargs)

    def _create_foreign_key_field(self, forms, **kwargs):
        """Creates a ForeignKeyField instance."""
        field_data = self._prepare_field_data()
        parent_form = forms.get(self.parent_endpoint)
        
        if not parent_form:
            raise ValueError(f'Parent form not found for endpoint: {self.parent_endpoint}')
        
        field_data.update({
            'parent_id': parent_form.id_field,
            'parent_label': parent_form.label_field,
            'parent_allow_new': parent_form.allow_children_make_new,
        })
        return ForeignKeyField(**field_data, **kwargs)

    def _prepare_field_data(self):
        """Prepares data common to all field types."""
        field_data = self.model_dump()
        return field_data

class Field(BaseField):
    """Represents a basic field within a form."""
    form_name: str
    form_endpoint: str

class ForeignKeyField(Field):
    """Represents a foreign-key field within a form."""
    parent_endpoint: str
    parent_id: str
    parent_label: str
    parent_allow_new: bool
