import streamlit as st
from src.types import Field, FieldType
from src.settings import logger
from src.api import APIClient
from datetime import date


class FormField:
    def __init__(self, field: Field, api_client: APIClient, endpoint: str):
        self.field = field
        self.api_client = api_client
        self.endpoint = endpoint
        self.is_new = False
        self.dropdown_options = {}

    def render(self):
        """Render the form field with two columns: left for checkbox/name, right for input."""
        left_col, right_col = st.columns([1, 2])
        
        with left_col:
            if self.field.type == FieldType.FOREIGN_KEY:
                self.is_new = st.checkbox(f'New {self.field.parent_endpoint}', key=f'{self.endpoint}-{self.field.name}-checkbox')
            else:
                st.write(f'*{self.field.form_name}*')  # Print the table name in italics

        with right_col:
            if self.is_new:
                return None  # Indicates that a child form should be rendered
            else:
                return self._render_field_input()

    def _render_field_input(self):
        """Render the appropriate input component based on the field type."""
        if self.field.type == FieldType.FOREIGN_KEY:
            return self._create_foreign_key_selectbox()
        else:
            return BaseForm.get_field_input_component(self.field, self.endpoint)

    def _create_foreign_key_selectbox(self):
        """Create a select box for a foreign key field."""
        if self.field.name not in self.dropdown_options:
            self._fetch_foreign_key_options()

        options = self.dropdown_options.get(self.field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(self._create_title(), options=labels, label_visibility='visible', key=f'{self.endpoint}-{self.field.name}')
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


class BaseForm:
    def __init__(self, api_client: APIClient, endpoint: str, fields: list[Field]):
        self.api_client = api_client
        self.endpoint = endpoint
        self.fields = [FormField(field, api_client, endpoint) for field in fields]
        self.child_forms = {}

    def show_form(self, operation: str = None):
        selected_operation = operation or st.radio("Select Operation", ["Create", "Update", "Delete"], key=self.endpoint)

        with st.container():
            item_id = None
            if selected_operation in ["Update", "Delete"]:
                item_id = st.number_input("Record (ID) to modify:", min_value=1)

            input_data = {}
            if selected_operation in ["Create", "Update"]:
                self._render_form_fields(input_data)

            submit_button = st.button("Submit", key=f'{self.endpoint}-submit')

        if submit_button:
            self._handle_submission(selected_operation, item_id, input_data)

    def _render_form_fields(self, input_data):
        """Render all form fields, including handling of child forms."""
        for form_field in self.fields:
            field_data = form_field.render()
            if form_field.is_new and field_data is None:
                child_data = self._render_child_form(form_field.field.parent_endpoint)
                input_data[form_field.field.name] = child_data
            else:
                input_data[form_field.field.name] = field_data

    def _render_child_form(self, endpoint: str):
        """Render a child form and return its input data."""
        if endpoint not in self.child_forms:
            child_form_class = forms.get(endpoint)
            if not child_form_class:
                raise ValueError(f"No form class found for endpoint: {endpoint}")
            self.child_forms[endpoint] = child_form_class(self.api_client)

        return self.child_forms[endpoint].show_form(operation="Create")

    def _handle_submission(self, operation, item_id, data):
        """Handle form submission based on the selected operation."""
        serializable_data = self._clean_any_dates(data)
        if operation == "Create":
            self.api_client.perform_crud(self.endpoint, "POST", data=serializable_data)
        elif operation == "Update":
            self.api_client.perform_crud(self.endpoint, "PUT", data=serializable_data, id=item_id)
        elif operation == "Delete":
            self.api_client.perform_crud(self.endpoint, "DELETE", id=item_id)

        self.api_client.clear_cache()
        st.rerun()

    @staticmethod
    def _clean_any_dates(data):
        """Convert date objects to isoformat strings for serialization."""
        cleaned_data = data.copy()
        for key, value in cleaned_data.items():
            if isinstance(value, date):
                cleaned_data[key] = value.isoformat()
        return cleaned_data

    @staticmethod
    def get_field_input_component(field: Field, endpoint: str):
        """Retrieve the appropriate input component for a field."""
        if field.type == FieldType.TEXT:
            return st.text_input(BaseForm._create_title(field), value=field.default, key=f'{endpoint}-{field.name}')
        elif field.type == FieldType.MULTILINE_TEXT:
            return st.text_area(BaseForm._create_title(field), value=field.default, key=f'{endpoint}-{field.name}')
        elif field.type == FieldType.NUMBER:
            return st.number_input(BaseForm._create_title(field), value=field.default, key=f'{endpoint}-{field.name}')
        elif field.type == FieldType.DATE:
            return st.date_input(BaseForm._create_title(field), value=field.default, key=f'{endpoint}-{field.name}')
        elif field.type == FieldType.BOOLEAN:
            return st.checkbox(BaseForm._create_title(field), value=field.default, key=f'{endpoint}-{field.name}')
        else:
            raise ValueError(f"Unsupported field type: {field.type}")

    @staticmethod
    def _create_title(field):
        title = f"**{field.name.replace('_', ' ').title()}**"
        return title + ' *' if field.is_required else title


# Define specific forms for each endpoint
class ResumeForm(BaseForm):
    name = 'resumes'
    fields_list = [
        Field(name='data', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class PostingForm(BaseForm):
    name = 'postings'
    fields_list = [
        Field(name='platform', type=FieldType.TEXT, is_required=True, form_name=name),
        Field(name='company', type=FieldType.TEXT, is_required=True, form_name=name),
        Field(name='title', type=FieldType.TEXT, is_required=True, form_name=name),
        Field(name='salary', type=FieldType.NUMBER, is_required=False, form_name=name),
        Field(name='description', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name),
        Field(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name),
        Field(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=False, form_name=name),
        Field(name='remote', type=FieldType.BOOLEAN, is_required=False, form_name=name),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ApplicationForm(BaseForm):
    name = 'applications'
    fields_list = [
        Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name=name),
        Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name=name),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name=name),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseTypeForm(BaseForm):
    name = 'response_types'
    fields_list = [
        Field(name='name', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseForm(BaseForm):
    name = 'responses'
    fields_list = [
        Field(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', parent_allow_new=True, form_name=name),
        Field(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', parent_allow_new=True, form_name=name),
        Field(name='date_received', type=FieldType.DATE, is_required=True, form_name=name),
        Field(name='data', type=FieldType.TEXT, is_required=False, form_name=name),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


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
