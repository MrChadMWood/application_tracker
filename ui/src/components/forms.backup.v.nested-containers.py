import streamlit as st
from src.types import Field, FieldType
from src.settings import logger
from src.api import APIClient
from datetime import date
from itertools import chain


class BaseForm:
    def __init__(self, api_client: APIClient, endpoint: str, fields: list[Field]):
        self.api_client: APIClient = api_client
        self.endpoint: str = endpoint
        self.dropdown_options: dict = {}
        self.new_item_flags = {}

        # Maintain a list of fields and their associated endpoints
        self._fields: dict[str, list[Field]] = {endpoint: fields}

    @property
    def fields(self) -> dict[str, list[Field]]:
        """Returns fields ordered by the dependency chain, if any."""
        return self._fields

    def collect_foreign_key_fields(self):
        """Collect all foreign key fields, including from child forms."""
        fk_fields = []
        for endpoint, fields in self.fields.items():
            for field in fields:
                if field.type == FieldType.FOREIGN_KEY:
                    fk_fields.append(field)
                    if field.parent_allow_new:
                        # Create a child form to check for its foreign key fields
                        child_form_class = forms.get(field.parent_endpoint)
                        if child_form_class:
                            child_form_instance = child_form_class(self.api_client)
                            fk_fields.extend(child_form_instance.collect_foreign_key_fields())
        return fk_fields

    def show_form(self, operation=None):
        selected_operation = operation

        if not operation:
            selected_operation = st.radio("Select Operation", ["Create", "Update", "Delete"], key=self.endpoint)

        with st.container():
            item_id = None
            if selected_operation in ["Update", "Delete"]:
                item_id = st.number_input("Record (ID) to modify:", min_value=1)

            input_data = {}
            if selected_operation in ["Create", "Update"]:
                # Loop over fields, ensuring that child fields are added dynamically if 'New' is selected
                for endpoint, fields in self.fields.items():
                    for field in fields:
                        if field.type == FieldType.FOREIGN_KEY and selected_operation == 'Create':
                            self.new_item_flags[field.name] = st.checkbox(f'New {field.parent_endpoint}', key=field.name)
                            if self.new_item_flags.get(field.name):
                                self._render_child_form(field, input_data)
                            else:
                                input_data[field.name] = self.get_field_input_component(field)
                        else:
                            input_data[field.name] = self.get_field_input_component(field)

            submit_button = st.button("Submit", key=f'{self.endpoint}-submit')

        if submit_button:
            self._handle_submission(selected_operation, None, input_data)


    def _render_child_form(self, field, input_data):
        """Render a child form if the 'New' checkbox is selected."""
        with st.container(border=True):
            child_form_class = forms[field.parent_endpoint]
            st.write(f"###### {child_form_class.name.title()}")
            child_form_instance = child_form_class(self.api_client)
            child_input_data = child_form_instance.show_form(operation='Create')
            input_data[field.name] = child_input_data

    def _clean_any_dates(self, data):
        """Convert date objects to isoformat strings for serialization."""
        cleaned_data = data.copy()
        for key, value in cleaned_data.items():
            if isinstance(value, date):
                cleaned_data[key] = value.isoformat()
        return cleaned_data

    def _handle_submission(self, operation, item_id, data):
        """Handle form submission based on selected operation."""
        serializable_data = self._clean_any_dates(data)
        if operation == "Create":
            self.api_client.perform_crud(self.endpoint, "POST", data=serializable_data)
        elif operation == "Update":
            self.api_client.perform_crud(self.endpoint, "PUT", data=serializable_data, id=item_id)
        elif operation == "Delete":
            self.api_client.perform_crud(self.endpoint, "DELETE", id=item_id)

        self.api_client.clear_cache()
        st.rerun()

    def get_field_input_component(self, field: Field):
        """Retrieve the appropriate input component for a field."""
        if field.type == FieldType.TEXT:
            return self._create_text_input(field)
        elif field.type == FieldType.MULTILINE_TEXT:
            return self._create_text_area(field)
        elif field.type == FieldType.NUMBER:
            return self._create_number_input(field)
        elif field.type == FieldType.DATE:
            return self._create_date_input(field)
        elif field.type == FieldType.BOOLEAN:
            return self._create_checkbox(field)
        elif field.type == FieldType.FOREIGN_KEY:
            return self._create_foreign_key_selectbox(field)
        else:
            raise ValueError(f"Unsupported field type: {field.type}")

    def _create_title(self, field):
        title = f"**{field.name.replace('_', ' ').title()}**"
        return title + ' *' if field.is_required else title

    def _create_text_input(self, field: Field):
        return st.text_input(self._create_title(field), value=field.default)

    def _create_text_area(self, field: Field):
        return st.text_area(self._create_title(field), value=field.default)

    def _create_number_input(self, field: Field):
        return st.number_input(self._create_title(field), value=field.default)

    def _create_date_input(self, field: Field):
        return st.date_input(self._create_title(field), value=field.default)

    def _create_checkbox(self, field: Field):
        return st.checkbox(self._create_title(field), value=field.default)

    def _create_foreign_key_selectbox(self, field: Field):
        if field.name not in self.dropdown_options:
            self._fetch_foreign_key_options(field)

        options = self.dropdown_options.get(field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(self._create_title(field), options=labels, label_visibility='visible')
        selected_id = self._get_selected_foreign_key_id(options, selected_label)
        return selected_id

    def _fetch_foreign_key_options(self, field: Field):
        """Fetch options for foreign key fields."""
        items = self.api_client.perform_crud(field.parent_endpoint, "GET")
        self.dropdown_options[field.name] = {
            item[field.parent_id]: item[field.parent_label] for item in items
        }

    def _get_selected_foreign_key_id(self, options, selected_label):
        for id_, label in options.items():
            if label == selected_label:
                return id_
        return None


# Define specific forms for each endpoint
class ResumeForm(BaseForm):
    name = 'resumes'
    fields_list: list[Field] = [
        Field(name='data', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class PostingForm(BaseForm):
    name = 'postings'
    fields_list: list[Field] = [
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
    fields_list: list[Field] = [
        Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name=name),
        Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name=name),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name=name),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseTypeForm(BaseForm):
    name = 'response_types'
    fields_list: list[Field] = [
        Field(name='name', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseForm(BaseForm):
    name = 'responses'
    fields_list: list[Field] = [
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
