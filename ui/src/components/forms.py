import streamlit as st
from src.types import Field, FieldType
from src.settings import logger
from datetime import date, datetime


class BaseForm:
    def __init__(self, api_client, endpoint, fields):
        self.api_client = api_client
        self.endpoint = endpoint
        self.fields = fields
        self.dropdown_options = {}
        self._validate_fields()

    def _validate_fields(self):
        field_names = [f.name for f in self.fields]
        if len(set(field_names)) != len(field_names):
            raise ValueError('Fields may not have duplicate names')

    def show_form(self):
        selected_operation = st.radio(
            "Select Operation",
            ["Create", "Update", "Delete"]
        )

        with st.form("crud_form"):
            item_id = None
            if selected_operation in ["Update", "Delete"]:
                item_id = st.number_input("Record (ID) to modify:", min_value=1)

            input_data = {}
            if selected_operation in ["Create", "Update"]:
                for field in self.fields:
                    input_data[field.name] = self.get_field_input_component(field)

            submit_button = st.form_submit_button("Submit")

        if submit_button:
            self._handle_submission(selected_operation, item_id, input_data)

    def _clean_any_dates(self, _data):
        data = _data.copy()
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
        return data

    def _handle_submission(self, operation, item_id, data):
        serializable_data = self._clean_any_dates(data)
        if operation == "Create":
            response = self.api_client.perform_crud(self.endpoint, "POST", data=serializable_data)
        elif operation == "Update":
            response = self.api_client.perform_crud(self.endpoint, "PUT", data=serializable_data, id=item_id)
        elif operation == "Delete":
            response = self.api_client.perform_crud(self.endpoint, "DELETE", id=item_id)

        self.api_client.clear_cache()
        st.rerun()

    def get_field_input_component(self, field: Field):
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
        selected_label = st.selectbox(self._create_title(field), options=labels)
        selected_id = self._get_selected_foreign_key_id(options, selected_label)
        return selected_id

    def _fetch_foreign_key_options(self, field: Field):
        items = self.api_client.perform_crud(field.parent_endpoint, "GET")
        self.dropdown_options[field.name] = {
            item[field.parent_id]: item[field.parent_label] for item in items
        }

    def _get_selected_foreign_key_id(self, options, selected_label):
        for id_, label in options.items():
            if label == selected_label:
                return id_
        return None

class ResumeForm(BaseForm):
    def __init__(self, api_client):
        fields = [Field(name='data', type=FieldType.TEXT, is_required=True)]
        super().__init__(api_client, "resumes", fields)

class JobPostingForm(BaseForm):
    def __init__(self, api_client):
        fields = [
            Field(name='platform', type=FieldType.TEXT, is_required=True),
            Field(name='company', type=FieldType.TEXT, is_required=True),
            Field(name='title', type=FieldType.TEXT, is_required=True),
            Field(name='salary', type=FieldType.NUMBER, is_required=False),
            Field(name='description', type=FieldType.MULTILINE_TEXT, is_required=False),
            Field(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=False),
            Field(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=False),
            Field(name='remote', type=FieldType.BOOLEAN, is_required=False),
        ]
        super().__init__(api_client, "postings", fields)

class JobApplicationForm(BaseForm):
    def __init__(self, api_client):
        fields = [
            Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_n=True),
            Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', include_create_button=True),
            Field(name='date_submitted', type=FieldType.DATE, is_required=True),
        ]
        super().__init__(api_client, "applications", fields)

class ResponseTypeForm(BaseForm):
    def __init__(self, api_client):
        fields = [Field(name='name', type=FieldType.TEXT, is_required=True)]
        super().__init__(api_client, "response_types", fields)

class ResponseForm(BaseForm):
    def __init__(self, api_client):
        fields = [
            Field(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', include_create_button=True),
            Field(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', include_create_button=True),
            Field(name='date_received', type=FieldType.DATE, is_required=True),
            Field(name='data', type=FieldType.TEXT, is_required=False),
        ]
        super().__init__(api_client, "responses", fields)

def create_form(api_client, endpoint):
    forms = {
        "resumes": ResumeForm,
        "postings": JobPostingForm,
        "applications": JobApplicationForm,
        "response_types": ResponseTypeForm,
        "responses": ResponseForm
    }
    form_class = forms.get(endpoint)
    if not form_class:
        raise ValueError(f"No form class found for endpoint: {endpoint}")
    return form_class(api_client)
