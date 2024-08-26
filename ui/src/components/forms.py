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
    def __init__(self, field: Field, api_client: APIClient, parent=None):
        self.field = field
        self.api_client = api_client
        self.is_new = False
        self.dropdown_options = {}
        self.pending_id_from = None  # Track if this field is pending a foreign key

    def render(self, fk_tracker: dict = None):
        """Render the form row with two columns."""
        fk_tracker = fk_tracker or {}
        left_col, right_col = st.columns([1, 3])

        with left_col:
            self._render_left_column(fk_tracker)

        with right_col:
            return self._render_right_column()

    def _render_left_column(self, fk_tracker):
        """Render the left column, handling the 'New' checkbox or displaying the field's name."""
        if self.field.type == FieldType.FOREIGN_KEY:
            self._handle_foreign_key_checkbox(fk_tracker)
        else:
            self._display_field_name()

    def _handle_foreign_key_checkbox(self, fk_tracker):
        """Handle the logic for the 'New' checkbox in foreign key fields."""
        self._initialize_foreign_key_tracker(fk_tracker)
        self.is_new = st.checkbox('New', key=f'{self.field.name}-checkbox')
        self._update_foreign_key_tracking(fk_tracker)

    def _initialize_foreign_key_tracker(self, fk_tracker):
        """Ensure that the foreign key tracker is initialized for this field's endpoint."""
        if not fk_tracker.get(self.field.form_endpoint):
            logger.info(f'Init tracking for {self.field.form_endpoint}')
            fk_tracker[self.field.form_endpoint] = set()

    def _update_foreign_key_tracking(self, fk_tracker):
        """Update the tracking of foreign key dependencies based on the 'New' checkbox."""
        endpoint_tracker = fk_tracker[self.field.form_endpoint]
        if self.is_new:
            self.pending_id_from = self.field.parent_endpoint
            endpoint_tracker[self.field.parent_endpoint] = self.field.name
            logger.info(f'FK tracker updated: {endpoint_tracker}')
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
            return DynamicForm.get_field_input_component(self.field)

    def _create_foreign_key_selectbox(self):
        """Create a selectbox; click behavior propogates additional fields."""
        if self.field.name not in self.dropdown_options:
            self._fetch_foreign_key_options()

        options = self.dropdown_options.get(self.field.name, {})
        labels = list(options.values())
        selected_label = st.selectbox(self._create_title(), options=labels, label_visibility='visible', key=f'{self.field.name}')
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

    def _create_title(self):
        title = f"**{self.field.name.replace('_', ' ').title()}**"
        return title + ' *' if self.field.is_required else title


class DynamicForm:
    '''
    A dynamic form that combines fields from multiple endpoints into a single form. The form dynamically adds related
    fields when a user selects the "New" checkbox for a foreign-key field. All fields are rendered in a single form with
    a unified submit button at the bottom.

    When new fields are added due to a foreign-key relationship, they are inserted immediately after the foreign key field.
    This is preservation of intuitive field order.

    There is some instability with FormRow positions while adding new fields. FieldRows whose position isn't changing, are
    bouncing around. This would ideally be fixed in a future update.

    The form collects all necessary data from the user and submits it in a single operation, ensuring that all records
    are processed in the correct order according to their dependencies.
    '''
    def __init__(self, api_client: APIClient, fields: list[Field]):
        self.api_client: APIClient = api_client # Used for data retrieval, employs caching
        self.input_data: dict[str, dict[str, object]] = {} # Maps form endpoints to each fields input
        self.rows: list[Field] = [] # Cache of all rows in form. Recalcd when rows change.
        self.pending_fk: dict[str, dict[str, str]] = {}  # Tracks foreign keys that need to be resolved
        self._initialize_rows(fields)

    def _initialize_rows(self, fields, insert_after=None):
        """Initialize the fields and structure for the nested data."""
        new_rows = []
        for field in fields:
            if field.form_endpoint not in self.pending_fk:
                self.pending_fk[field.form_endpoint] = {}

            # Track foreign key fields that may need resolution
            if field.type == FieldType.FOREIGN_KEY:
                self.pending_fk[field.form_endpoint][field.parent_endpoint] = None

            # Track input data
            if field.form_name not in self.input_data:
                self.input_data[field.form_endpoint] = {}
            
            row = FormRow(field, self.api_client)
            new_rows.append(row)

        # Preserves field order by inserting at location
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
        for i, row in enumerate(self.rows):
            field_data = row.render(fk_tracker=self.pending_fk)
            if row.is_new and field_data is None:
                # Adds fields to self.rows, after current iteration
                self._add_child_rows(row.field.parent_endpoint, insert_after=i)
            else:
                self.input_data[row.field.form_endpoint][row.field.name] = field_data

    def _add_child_rows(self, parent_endpoint, insert_after):
        """Add fields from a child endpoint dynamically to the form."""
        child_form_class = forms.get(parent_endpoint)
        if not child_form_class:
            raise ValueError(f"No form class found for endpoint: {parent_endpoint}")

        child_form = child_form_class(self.api_client)
        self._initialize_rows(child_form.fields_list, insert_after=insert_after)

    def _supply_any_pending_ids(self, endpoint, data, foreign_keys):
        """Inject any necessary foreign key values into the submission data."""
        pending_for_endpoint = self.pending_fk[endpoint]
        logger.info(f'Endpoint {endpoint} requires: {pending_for_endpoint}')
        
        for parent_endpoint, pending_fk in pending_for_endpoint.items():
            parent_id = foreign_keys.get(parent_endpoint)
            if parent_id is not None:
                data[pending_fk] = parent_id
                logger.info(f'Injected {parent_id} into {pending_fk} for {endpoint}.')
            else:
                raise KeyError(f'Missing foreign key for {pending_fk} in {endpoint}. Foreign_keys: {pending_for_endpoint}')

        return data

    def _handle_submission(self):
        """Handle form submission."""
        serializable_data = self._clean_any_dates(self.input_data)
        logger.info(f'Serializable data before submission: {serializable_data}')
        
        foreign_keys = {}
        # Submit all collected data in the correct order
        for endpoint, raw_data in reversed(serializable_data.items()):
            if raw_data:
                ready_data = self._supply_any_pending_ids(endpoint, raw_data, foreign_keys)
                logger.info(f'Sending {endpoint} data: {ready_data}')
                response = self.api_client.perform_crud(endpoint, "POST", data=ready_data)
                foreign_keys[endpoint] = response.get('id')

        logger.info(f'Current FKs: {foreign_keys}')
        self.api_client.clear_cache()
        st.rerun()

    def _get_row(self, endpoint, field_name):
        """Retrieve a Field object by its name."""
        for row in self.rows:
            if row.field.form_endpoint == endpoint and row.field.name == field_name:
                return row
        return None

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
