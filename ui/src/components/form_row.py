# ./src/components/form_row.py
import streamlit as st
from src.schemas import Field, FieldType
from src.api import APIClient
import logging

logger = logging.getLogger(__name__)


def create_title(field):
    """Generate the title for a form field, formatted with bold and optional asterisk."""
    title = f"**{field.name.replace('_', ' ').title()}**"
    return f"{title} *" if field.is_required else title

def get_field_input_component(field: Field):
    """Retrieve the Streamlit input component corresponding to the field's type."""
    component_map = {
        FieldType.TEXT: st.text_input,
        FieldType.MULTILINE_TEXT: st.text_area,
        FieldType.NUMBER: st.number_input,
        FieldType.DATE: st.date_input,
        FieldType.BOOLEAN: st.checkbox
    }
    component_func = component_map.get(field.type)
    if not component_func:
        raise ValueError(f"Unsupported field type: {field.type}")
    return component_func(create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')

class FormRow:
    """
    Represents a row within a form, consisting of a label and an input field.

    Each `FormRow` is rendered as two columns:
    - The left column displays either a "New" checkbox (for foreign-key fields) or the parent table's name.
    - The right column contains the actual input field or a placeholder when "New" is selected.

    Attributes:
        field (Field): The field object representing the form field.
        api_client (APIClient): The API client used to retrieve data for foreign-key fields.
        is_new (bool): Indicates whether the "New" checkbox is selected for a foreign-key field.
        dropdown_options (dict): Stores options for foreign-key selectboxes.
        pending_id_from (str): Tracks the parent endpoint if the field is awaiting a foreign key ID.
    """
    def __init__(self, field: Field, api_client: APIClient, parent=None):
        self.field = field
        self.api_client = api_client
        self.is_new = False
        self.dropdown_options = {}
        self.pending_id_from = None  # Track if this field is pending a foreign key

    def render(self, fk_tracker: dict = None, allow_new: bool = True):
        """Render the form row with two columns."""
        fk_tracker = fk_tracker or {}
        _, left_col, right_col = st.columns([.2, 4, 8], vertical_alignment='bottom')

        with left_col:
            self._render_left_column(fk_tracker, allow_new=allow_new)

        with right_col:
            return self._render_right_column()

    def _render_left_column(self, fk_tracker, allow_new):
        """Render the left column, handling the 'New' checkbox or displaying the field's name."""
        if allow_new and self.field.type == FieldType.FOREIGN_KEY:
            is_new = self._handle_foreign_key_checkbox(fk_tracker)
            if not is_new:
                self._display_field_name()
        else:
            self._display_field_name()

    def _handle_foreign_key_checkbox(self, fk_tracker):
        """Handle the logic for the 'New' checkbox in foreign key fields."""
        self.is_new = st.checkbox(f'New {self.field.parent_endpoint}', key=f'{self.field.name}-checkbox')
        self._update_foreign_key_tracking(fk_tracker)
        return self.is_new

    def _update_foreign_key_tracking(self, fk_tracker):
        """Update the tracking of foreign key dependencies based on the 'New' checkbox."""
        endpoint_tracker = fk_tracker[self.field.form_endpoint]
        if self.is_new:
            self.pending_id_from = self.field.parent_endpoint
            endpoint_tracker[self.field.parent_endpoint] = self.field.name
        else:
            endpoint_tracker.pop(self.field.parent_endpoint, None)
            self.pending_id_from = None

    def _display_field_name(self):
        """Display the field's name in italic in the left column."""
        st.write(f'*{self.field.form_name}*')

    def _render_right_column(self):
        """Render the right column, displaying either the input field or a placeholder."""
        if self.is_new:
            st.write(f'###### *Creating new {self.field.parent_endpoint}*')
            return None
        return self._render_field_input()

    def _render_field_input(self):
        """Render the input component based on the field type."""
        if self.field.type == FieldType.FOREIGN_KEY:
            return self._create_foreign_key_selectbox()
        else:
            return get_field_input_component(self.field)

    def _create_foreign_key_selectbox(self):
        """Create a selectbox; click behavior propogates additional fields."""
        if self.field.name not in self.dropdown_options:
            self._fetch_foreign_key_options()

        options = self.dropdown_options.get(self.field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(create_title(self.field), options=labels, label_visibility='visible', key=f'{self.field.name}')
        selected_id = self._get_selected_foreign_key_id(options, selected_label)
        return selected_id

    def _fetch_foreign_key_options(self):
        items = self.api_client.perform_crud(self.field.parent_endpoint, "GET")
        self.dropdown_options[self.field.name] = {
            item[self.field.parent_id]: item[self.field.parent_label] for item in items
        }

    def _get_selected_foreign_key_id(self, options, selected_label):
        for id_, label in options.items():
            if label == selected_label:
                return id_
        return None
