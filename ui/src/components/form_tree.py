# ./src/components/form_tree.py
import streamlit as st
from src.schemas import Field, FieldType
from src.components.form_row import FormRow
from src.api import APIClient
from datetime import date
import logging

logger = logging.getLogger(__name__)


class FormTree:
    """
    Manages the initialization, rendering, tracking, and submission of form fields.

    The `FormTree` organizes a logical hierarchy of forms that allows users to expand
    foreign-key fields into the forms of related records. It ensures that forms are
    submitted in the correct order by leveraging the implicit ordering of dictionary keys.
    This structure appears as a flat list of fields to the user, but operates as a tree
    of nested forms behind the scenes.
    """

    def __init__(self, api_client: APIClient, fields: list[Field], forms):
        """
        Initializes the FormTree with a set of fields and their corresponding forms.

        Args:
            api_client (APIClient): A client to interact with the API for data retrieval and submission.
            fields (list[Field]): A list of `Field` objects that represent the form fields.
            forms (dict): A dictionary mapping form endpoints to their corresponding `FormTree` child class instances.

        Attributes:
            api_client (APIClient): An instance of the API client used for data operations.
            fields (list[Field]): The list of `Field` objects to be rendered in the form.
            forms (dict): Maps form endpoints to their respective `FormTree` instances.
            rows (list[FormRow]): A list of `FormRow` objects representing each row in the form.
            pending_fk (dict): Tracks foreign-key fields that need to have their IDs injected after API responses.
            input_data (dict): Stores the user input data, keyed by form endpoint and field name.
        """
        self.api_client: APIClient = api_client
        self.fields: list[Field] = fields
        self.forms: dict[str, type[FormTree]] = forms
        self.rows: list[FormRow] = []
        self.pending_fk: dict[str, dict[str, str]] = {}
        self.input_data: dict[str, dict[str, int | float | str | date]] = {}
        self.selected_operation: str | None = None
        self.record_id: int | None = None
        self.initialize_fields(fields)

    def show_form(self):
        """Render the form, allow operation selection, and handle submission."""
        # Reset pending foreign key tracking
        self.pending_fk = {endpoint: {} for endpoint in self.forms.keys()}

        self.selected_operation = st.radio('Select operation:', options=["Create", "Update", "Delete"], key='operation-select', horizontal=True)

        if self.selected_operation in ["Update", "Delete"]:
            self.record_id = st.number_input("Record (ID) to modify:", min_value=1)
            st.write('___')

        if self.selected_operation != "Delete":
            self.render_rows()

        if st.button("Submit", key='form-submit'):
            self.submit()

    def initialize_fields(self, fields, insert_after=None):
        """Initialize the fields, adding to end or after specified index."""
        new_rows = [self.create_row(field) for field in fields]
        if insert_after is None:
            self.rows.extend(new_rows)
        else:
            self.rows[insert_after + 1:insert_after + 1] = new_rows

    def create_row(self, field):
        """Create a FormRow and track any foreign keys."""
        if field.form_endpoint not in self.pending_fk:
            self.pending_fk[field.form_endpoint] = {}

        if field.type == FieldType.FOREIGN_KEY:
            self.pending_fk[field.form_endpoint][field.parent_endpoint] = None

        if field.form_name not in self.input_data:
            self.input_data[field.form_endpoint] = {}

        return FormRow(field, self.api_client)

    def render_rows(self):
        """Render form rows and track input data."""
        is_op_create = self.selected_operation=='Create'
        for i, row in enumerate(self.rows):
            field_data = row.render(fk_tracker=self.pending_fk, allow_new=is_op_create)
            if row.is_new and field_data is None:
                self.add_child_rows(row.field.parent_endpoint, insert_after=i)
            else:
                self.input_data[row.field.form_endpoint][row.field.name] = field_data
            
            # Creates line under each row.
            st.write('___')

    def add_child_rows(self, parent_endpoint, insert_after):
        """Add fields from a child endpoint dynamically to the form."""
        child_form_class = self.forms.get(parent_endpoint)
        if not child_form_class:
            raise ValueError(f"No form class found for endpoint: {parent_endpoint}")

        self.initialize_fields(child_form_class.fields_list, insert_after=insert_after)

    def get_row(self, endpoint, field_name):
        """Retrieve a Field object by its name."""
        for row in self.rows:
            if row.field.form_endpoint == endpoint and row.field.name == field_name:
                return row
        return None

    def submit(self):
        """Submit the form data to the API."""
        if self.selected_operation == "Delete":
            self.api_client.perform_crud(self.fields[0].form_endpoint, "DELETE", id=self.record_id)
        else:
            serializable_data = self.clean_any_dates(self.input_data)
            foreign_keys = {}
            for endpoint, raw_data in reversed(serializable_data.items()):
                if raw_data:
                    ready_data = self.supply_pending_ids(endpoint, raw_data, foreign_keys)
                    if self.selected_operation == "Create":
                        response = self.api_client.perform_crud(endpoint, "POST", data=ready_data)
                    elif self.selected_operation == "Update":
                        response = self.api_client.perform_crud(endpoint, "PUT", data=ready_data, id=self.record_id)
                    foreign_keys[endpoint] = response.get('id')

        self.api_client.clear_cache()
        st.rerun()

    def supply_pending_ids(self, endpoint, data, foreign_keys):
        """Inject necessary foreign key values into the data."""
        pending_for_endpoint = self.pending_fk.get(endpoint, {})
        for parent_endpoint, pending_fk in pending_for_endpoint.items():
            parent_id = foreign_keys.get(parent_endpoint)
            if parent_id:
                data[pending_fk] = parent_id
            else:
                raise KeyError(f'Missing foreign key for {pending_fk} in {endpoint}.')
        return data

    @staticmethod
    def clean_any_dates(data):
        """Convert date objects to ISO format strings."""
        for endpoint, fields in data.items():
            for key, value in fields.items():
                if isinstance(value, date):
                    fields[key] = value.isoformat()
        return data