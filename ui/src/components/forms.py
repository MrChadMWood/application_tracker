import streamlit as st
from src.schemas import Field, FieldType
# from src.components import FormRow (todo: refactor the components)
from src.settings import logger
from src.api import APIClient
from datetime import date


class FormRow:
    '''
    A component representing a row in the form. It contains two columns:
    - The left column is for a "New" checkbox next to foreign-key fields or displays the field's parent table's name.
    - The right column is for the input field itself.

    When the "New" checkbox is selected for a foreign-key field, the foreign-key field in the right column is replaced
    with a placeholder text ("Creating new {parent table name}"). This signals that new fields related to the foreign
    key should be dynamically inserted into the form.

    In a future update, the FormRow would ideally have a fixed height.
    '''
    def __init__(self, field: Field, api_client: APIClient):
        self.field = field
        self.api_client = api_client
        self.is_new = False
        self.dropdown_options = {}

    def render(self):
        """Render the form field with two columns: left for checkbox/name, right for input."""
        left_col, right_col = st.columns([1, 3])
        
        with left_col:
            if self.field.type == FieldType.FOREIGN_KEY:
                self.is_new = st.checkbox(f'New', key=f'{self.field.name}-checkbox')
            else:
                st.write(f'*{self.field.form_name}*')  # Print the table name in italics

        with right_col:
            if self.is_new:
                st.write(f'###### *Creating new {self.field.parent_endpoint}*')
                return None  # Indicates that a new entity is being created
            else:
                return self._render_field_input()

    def _render_field_input(self):
        """Render the input component based on the field type."""
        if self.field.type == FieldType.FOREIGN_KEY:
            return self._create_foreign_key_selectbox()
        else:
            return DynamicForm.get_field_input_component(self.field)

    def _create_foreign_key_selectbox(self):
        """Create a select box for a foreign key field."""
        if self.field.name not in self.dropdown_options:
            self._fetch_foreign_key_options()

        options = self.dropdown_options.get(self.field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(self._create_title(), options=labels, label_visibility='visible', key=f'{self.field.name}')
        selected_id = self._get_selected_foreign_key_id(options, selected_label)
        return selected_id

    def _fetch_foreign_key_options(self):
        """Fetch options for foreign key fields."""
        items = self.api_client.perform_crud(self.field.parent_endpoint, "GET")
        self.dropdown_options[self.field.name] = {
            item[self.field.parent_id]: item[self.field.parent_label] for item in items
        }

    def _get_selected_foreign_key_id(self, options, selected_label):
        for id_, label in options.items():
            if label == selected_label:
                return id_
        return None

    def _create_title(self):
        title = f"**{self.field.name.replace('_', ' ').title()}**"
        return title + ' *' if self.field.is_required else title


class DynamicForm:
    '''
    A dynamic form that combines fields from multiple endpoints into a single form. The form dynamically adds related
    fields when a user selects the "New" checkbox for a foreign-key field. All fields are rendered in a single form with
    a unified submit button at the bottom.

    This form does not preserve the order of fields. When new fields are added due to a foreign-key relationship, they are
    inserted at the end of the form. In a future update, it is prefered that new fields join immediately after the triggering 
    foreign-key field, pushing subsequent fields down in the form.

    There is some instability with FormRow positions while adding new fields. FieldRows whose position isn't changing, are
    bouncing around. This would ideally be fixed in a future update.

    The form collects all necessary data from the user and submits it in a single operation, ensuring that all records
    are processed in the correct order according to their dependencies.
    '''
    def __init__(self, api_client: APIClient, fields: list[Field]):
        self.api_client = api_client # Used for data retrieval, employs caching
        self.endpoints_data = {} # Maps form endpoints to their input data
        self.rows = [] # Cache of all rows in form. Recalcd when rows change.
        self._initialize_rows(fields)

    def _initialize_rows(self, fields, insert_after=None):
        """Initialize the fields and structure for the nested data."""
        new_rows = []
        for field in fields:
            if field.form_name not in self.endpoints_data:
                self.endpoints_data[field.form_endpoint] = {}
            new_rows.append(FormRow(field, self.api_client))

        if insert_after == None:
            self.rows.extend(new_rows)
        else:
            pos = insert_after + 1
            self.rows[pos:pos] = new_rows  

    def show_form(self):
        """Render form with all fields and submit button."""
        self._render_form_rows()

        submit_button = st.button("Submit", key='form-submit')

        if submit_button:
            self._handle_submission()

    def _render_form_rows(self):
        """Render all form fields, dynamically including related fields."""
        for i, form_row in enumerate(self.rows):
            field_data = form_row.render()
            if form_row.is_new and field_data is None:
                # Adds fields to self.rows, after current iteration
                self._add_child_rows(form_row.field.parent_endpoint, insert_after=i)
            else:
                self.endpoints_data[form_row.field.form_endpoint][form_row.field.name] = field_data

    def _add_child_rows(self, parent_endpoint, insert_after):
        """Add fields from a child endpoint dynamically to the form."""
        child_form_class = forms.get(parent_endpoint)
        if not child_form_class:
            raise ValueError(f"No form class found for endpoint: {parent_endpoint}")

        child_form = child_form_class(self.api_client)
        self._initialize_rows(child_form.fields_list, insert_after=insert_after)

    def _handle_submission(self):
        """Handle form submission."""
        serializable_data = self._clean_any_dates(self.endpoints_data)
        
        # Submit all collected data in the correct order
        for endpoint, data in serializable_data.items():
            if data:
                logger.info(f'submitting: {data}')
                self.api_client.perform_crud(endpoint, "POST", data=data)

        self.api_client.clear_cache()
        st.rerun()

    @staticmethod
    def _clean_any_dates(data):
        """Convert date objects to isoformat strings for serialization."""
        cleaned_data = {}
        for endpoint, fields in data.items():
            cleaned_fields = fields.copy()
            for key, value in cleaned_fields.items():
                if isinstance(value, date):
                    cleaned_fields[key] = value.isoformat()
            cleaned_data[endpoint] = cleaned_fields
        return cleaned_data

    @staticmethod
    def get_field_input_component(field: Field):
        """Retrieve the input component for a field."""
        if field.type == FieldType.TEXT:
            return st.text_input(DynamicForm._create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')
        elif field.type == FieldType.MULTILINE_TEXT:
            return st.text_area(DynamicForm._create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')
        elif field.type == FieldType.NUMBER:
            return st.number_input(DynamicForm._create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')
        elif field.type == FieldType.DATE:
            return st.date_input(DynamicForm._create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')
        elif field.type == FieldType.BOOLEAN:
            return st.checkbox(DynamicForm._create_title(field), value=field.default, key=f'{field.form_name}-{field.name}')
        else:
            raise ValueError(f"Unsupported field type: {field.type}")

    @staticmethod
    def _create_title(field):
        title = f"**{field.name.replace('_', ' ').title()}**"
        return title + ' *' if field.is_required else title


# Define specific forms for each endpoint
class ResumeForm(DynamicForm):
    name = 'resumes'
    endpoint = 'resumes'
    fields_list = [
        Field(name='data', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.fields_list)


class PostingForm(DynamicForm):
    name = 'posting'
    endpoint = 'postings'
    fields_list = [
        Field(name='platform', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint),
        Field(name='company', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint),
        Field(name='title', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint),
        Field(name='salary', type=FieldType.NUMBER, is_required=False, form_name=name, form_endpoint=endpoint),
        Field(name='description', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name, form_endpoint=endpoint),
        Field(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name, form_endpoint=endpoint),
        Field(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name, form_endpoint=endpoint),
        Field(name='remote', type=FieldType.BOOLEAN, is_required=False, form_name=name, form_endpoint=endpoint),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.fields_list)


class ApplicationForm(DynamicForm):
    name = 'application'
    endpoint = 'applications'
    fields_list = [
        Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name=name, form_endpoint=endpoint),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.fields_list)


class ResponseTypeForm(DynamicForm):
    name = 'response_type'
    endpoint = 'response_types'
    fields_list = [
        Field(name='name', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.fields_list)


class ResponseForm(DynamicForm):
    name = 'response'
    endpoint = 'responses'
    fields_list = [
        Field(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='date_received', type=FieldType.DATE, is_required=True, form_name=name, form_endpoint=endpoint),
        Field(name='data', type=FieldType.TEXT, is_required=False, form_name=name, form_endpoint=endpoint),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.fields_list)


# Factory function to create form instances
forms = {
    "resumes": ResumeForm,
    "postings": PostingForm,
    "applications": ApplicationForm,
    "response_types": ResponseTypeForm,
    "responses": ResponseForm
}


def create_form(api_client, endpoint):
    form_class = forms.get(endpoint)
    if not form_class:
        raise ValueError(f"No form class found for endpoint: {endpoint}")
    return form_class(api_client)
