import streamlit as st
from src.types import Field, FieldType
from src.settings import logger
from src.api import APIClient
from datetime import date

class BaseForm:
    def __init__(self, api_client: APIClient, endpoint: str, fields: list[Field]):
        self.api_client: APIClient = api_client
        self.endpoint: str = endpoint
        self.dropdown_options: dict = {}
        self.new_item_flags = {}

        # Maintain a list of fields and their associated endpoints
        self.fields: dict[str, list[Field]] = {endpoint: fields}
        self.ordered_fields: dict[tuple[int, str], Field] = {
            (i, endpoint): field for i, field in enumerate(fields)
        }

        # A collection of fields in columns, representing the rows in the form
        self.rows = []

    def show_form(self, operation: str = None):
        selected_operation = operation
        self.new_item_flags.clear()

        if not operation:
            selected_operation = st.radio("Select Operation", ["Create", "Update", "Delete"], key=self.endpoint)

        with st.container():
            item_id = None
            if selected_operation in ["Update", "Delete"]:
                item_id = st.number_input("Record (ID) to modify:", min_value=1)

            input_data = {}
            if selected_operation in ["Create", "Update"]:
                self._build_rows(selected_operation)
                self._render_rows(input_data)

            submit_button = st.button("Submit", key=f'{self.endpoint}-submit')

        if submit_button:
            self._handle_submission(selected_operation, item_id, input_data)

    def _build_rows(self, selected_operation):
        """Build the rows structure based on the current fields."""
        for (index, endpoint), field in sorted(self.ordered_fields.items()):
            if field.type == FieldType.FOREIGN_KEY and selected_operation == 'Create':
                # Foreign key fields are handled specially to potentially add child forms
                left_col, right_col = st.columns([1, 3])
                self.rows.append((left_col, right_col, field))

                with left_col:
                    self.new_item_flags[field.name] = st.checkbox(f'New {field.parent_endpoint}', key=f'{self.endpoint}-{field.name}-checkbox')
                
                if self.new_item_flags.get(field.name):
                    # Add child form fields in place of the foreign key field
                    new_fields = self._add_child_form(field.parent_endpoint, (index, endpoint))
                    for new_field in new_fields.values():
                        left_col, right_col = st.columns([1, 3])
                        self.rows.append((left_col, right_col, new_field))
                    continue  # Skip the original foreign key field if child form is added

            # For regular fields, add to rows
            left_col, right_col = st.columns([1, 3])
            self.rows.append((left_col, right_col, field))

    def _render_rows(self, input_data):
        """Render the rows built by _build_rows."""
        for left_col, right_col, field in self.rows:
            with right_col:
                input_data[field.name] = self.get_field_input_component(field)
            if not field.type == FieldType.FOREIGN_KEY:
                with left_col:
                    st.write(f'*{field.form_name}*')

    def _render_standard_field(self, field, input_data):
        """Render a standard field."""
        return self.get_field_input_component(field)

    def _add_child_form(self, endpoint: str, inplaceof: tuple[int, str]):
        """Adds a child form by dynamically adjusting the class fields."""
        start_index = inplaceof[0]

        # Get the fields from the child form's endpoint
        fields = forms[endpoint].fields_list
        self.fields[endpoint] = fields

        # Create new fields to be inserted
        new_fields = {(i + start_index + 1, endpoint): field for i, field in enumerate(fields)}

        # Adjust ordered fields to accommodate the new fields
        self.ordered_fields = {
            (i if i <= start_index else i + len(new_fields), e): f
            for (i, e), f in self.ordered_fields.items()
        }

        # Insert the new fields into the ordered fields
        self.ordered_fields.update(new_fields)
        return new_fields

    def _remove_child_form(self, endpoint: str):
        """Removes a child form by taking out its self.fields entry and re-compiling the ordered_fields."""
        # Remove fields associated with the endpoint from fields and ordered_fields
        if endpoint in self.fields:
            del self.fields[endpoint]

        # Rebuild ordered_fields without the child form fields
        self.ordered_fields = {
            k: field for k, field in self.ordered_fields.items()
            if k[1] != endpoint
        }

        # Re-index the ordered fields
        reindexed_ordered_fields = {}
        current_index = 0
        for (index, ep), field in sorted(self.ordered_fields.items()):
            reindexed_ordered_fields[(current_index, ep)] = field
            current_index += 1

        self.ordered_fields = reindexed_ordered_fields

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

    def _clean_any_dates(self, data):
        """Convert date objects to isoformat strings for serialization."""
        cleaned_data = data.copy()
        for key, value in cleaned_data.items():
            if isinstance(value, date):
                cleaned_data[key] = value.isoformat()
        return cleaned_data

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
        return st.text_input(self._create_title(field), value=field.default, key=f'{self.endpoint}-{field.name}')

    def _create_text_area(self, field: Field):
        return st.text_area(self._create_title(field), value=field.default, key=f'{self.endpoint}-{field.name}')

    def _create_number_input(self, field: Field):
        return st.number_input(self._create_title(field), value=field.default, key=f'{self.endpoint}-{field.name}')

    def _create_date_input(self, field: Field):
        return st.date_input(self._create_title(field), value=field.default, key=f'{self.endpoint}-{field.name}')

    def _create_checkbox(self, field: Field):
        return st.checkbox(self._create_title(field), value=field.default, key=f'{self.endpoint}-{field.name}')

    def _create_foreign_key_selectbox(self, field: Field):
        if field.name not in self.dropdown_options:
            self._fetch_foreign_key_options(field)

        options = self.dropdown_options.get(field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(self._create_title(field), options=labels, label_visibility='visible', key=f'{self.endpoint}-{field.name}')
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
    name = 'resume'
    endpoint = 'resumes'
    fields_list: list[Field] = [
        Field(name='data', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class PostingForm(BaseForm):
    name = 'posting'
    endpoint = 'postings'
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
    name = 'application'
    endpoint = 'applications'
    fields_list: list[Field] = [
        Field(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name=name),
        Field(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name=name),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name=name),
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseTypeForm(BaseForm):
    name = 'response_type'
    endpoint = 'response_types'
    fields_list: list[Field] = [
        Field(name='name', type=FieldType.TEXT, is_required=True, form_name=name)
    ]

    def __init__(self, api_client):
        super().__init__(api_client, self.name, self.fields_list)


class ResponseForm(BaseForm):
    name = 'response'
    endpoint = 'responses'
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
