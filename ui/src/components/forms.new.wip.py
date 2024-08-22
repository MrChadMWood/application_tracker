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

        # Stores child forms and their respective endpoints
        self._endpoints: list[str] = [endpoint]
        self._fields: dict[str, list[Field]] = {endpoint: fields}

    @property
    def fields(self) -> dict[str, list[Field]]:
        # Returns fields ordered by self.endpoints list
        index_map = {e: i for i, e in enumerate(self._endpoints)}
        return dict(sorted(self._fields.items(), key=lambda item: index_map[item[0]]))

    def add_fields(self, endpoint: str, fields: list[Field], after_entry: str = None):
        field_names = [f.name for f in fields]
        if len(set(field_names)) != len(field_names):
            raise ValueError('Fields may not have duplicate names')
        if not after_entry:
            self._endpoints.append(endpoint)
            self._fields[endpoint] = fields
        else:
            # Adds endpoint after given element
            index = self._endpoints.index(after_entry) + 1
            self._endpoints[index:index] = [endpoint]
            self._fields[endpoint] = fields

    def remove_fields(self, endpoint: str):
        self._endpoints.remove(endpoint)
        return self._fields.pop(endpoint)

    def show_form(self):
        selected_operation = st.radio(
            "Select Operation",
            ["Create", "Update", "Delete"]
        )

        with st.form("crud_form"):
            form_data = {}
            for endpoint in self._endpoints:
                st.subheader(f"Form for {endpoint.capitalize()}")

                item_id = None
                if selected_operation in ["Update", "Delete"]:
                    item_id = st.number_input(f"Record (ID) to modify for {endpoint}:", min_value=1)

                if selected_operation in ["Create", "Update"]:
                    input_data = {}
                    for field in self.fields[endpoint]:
                        if field.type == FieldType.FOREIGN_KEY:
                            left_side, right_side = st.columns([5, 1])
                            with right_side:
                                creating_new = st.checkbox('New', key=f"{endpoint}_{field.name}_new")
                            with left_side:
                                if creating_new:
                                    input_data[field.name] = self.get_field_input_component(field)
                                else:
                                    input_data[field.name] = self.get_field_input_component(field)
                        else:
                            input_data[field.name] = self.get_field_input_component(field)

                    form_data[endpoint] = {
                        "item_id": item_id,
                        "data": input_data
                    }

            submit_button = st.form_submit_button("Submit")

        if submit_button:
            self._handle_submission(selected_operation, form_data)

    def _clean_any_dates(self, _data):
        data = _data.copy()
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
        return data

    def _handle_submission(self, operation, data):
        for endpoint in self._endpoints:
            form_data = data.get(endpoint)
            if not form_data:
                continue

            item_id = form_data["item_id"]
            serializable_data = self._clean_any_dates(form_data["data"])
            if operation == "Create":
                self.api_client.perform_crud(endpoint, "POST", data=serializable_data)
            elif operation == "Update":
                self.api_client.perform_crud(endpoint, "PUT", data=serializable_data, id=item_id)
            elif operation == "Delete":
                self.api_client.perform_crud(endpoint, "DELETE", id=item_id)

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
    name = 'resumes'
    fields_list: list[Field] = [
        Field(name='data', type=FieldType.TEXT, is_required=True)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)

class PostingForm(BaseForm):
    name = 'postings'
    fields_list: list[Field] = [
        Field(name='platform', type=FieldType.TEXT, is_required=True),
        Field(name='company', type=FieldType.TEXT, is_required=True),
        Field(name='title', type=FieldType.TEXT, is_required=True),
        Field(name='salary', type=FieldType.NUMBER, is_required=False),
        Field(name='description', type=FieldType.MULTILINE_TEXT, is_required=False),
        Field(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=False),
        Field(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=False),
        Field(name='remote', type=FieldType.BOOLEAN, is_required=False),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)

class ApplicationForm(BaseForm):
    name = 'applications'
    fields_list: list[Field] = [
        Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True),
        Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)

class ResponseTypeForm(BaseForm):
    name = 'response_types'
    fields_list: list[Field] = [
        Field(name='name', type=FieldType.TEXT, is_required=True)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)

class ResponseForm(BaseForm):
    name = 'responses'
    fields_list: list[Field] = [
        Field(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', parent_allow_new=True),
        Field(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', parent_allow_new=True),
        Field(name='date_received', type=FieldType.DATE, is_required=True),
        Field(name='data', type=FieldType.TEXT, is_required=False),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)

def create_form(api_client, endpoint):
    forms = {
        "resumes": ResumeForm,
        "postings": PostingForm,
        "applications": ApplicationForm,
        "response_types": ResponseTypeForm,
        "responses": ResponseForm
    }
    form_class = forms.get(endpoint)
    if not form_class:
        raise ValueError(f"No form class found for endpoint: {endpoint}")
    return form_class(api_client)
