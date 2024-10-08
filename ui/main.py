import streamlit as st
import logging
from src.settings import api_url, layout_mode
from src.schemas import Field, ForeignKeyField, FieldType, FieldTemplate
from src.components.form import Form, FormTree
from src.components.table import TableDisplay
from src.components.crud import DynamicCRUDForm
from src.api import APIClient

logger = logging.getLogger(__name__)

# Assigned a value due to streamlit magic otherwise embedding string into webapp.
todo = '''
TODO:
    A recent change updated Form class to include `id_field` as an attribute. Older code assumed that `"id"` was the id field on a db table belonging to a form, rather than relying on a variable.
    As a result of this change, older code should be updated to reference the `id_field` attribute. Any reference to form labels should similarly utilize the `label_field` attribute.

    The form could implement better behavior for required fields by refusing submission if they do not have a default.
    Need to test allow_children_make_new=False
    Need to implement better label fields in the DB. Consider generated stored columns.

    Make the forms `id` field in Update and Delete operations autopopulate via click on a row in data table. For update, make all row data load into form.

    The use of "endpoint" might be a bit confusing.

    Would be neat if the data display table could show alternative tables, so that a denormalized view can be shown instead.

    The "New" checkbox would benefit from having an attribute like "parent_form_name", which would be more clear than using "parent_endpoint"
    the `id_field` and `label_field` could have more explicit names.
'''

def create_forms():
    ResumeForm = Form(
        name='resume',
        endpoint='resumes',
        id_field='id',
        label_field='data',
        allow_children_make_new=True,
        fields_list=[
            FieldTemplate(name='data', type=FieldType.TEXT, is_required=True)
        ],
    )

    PostingForm = Form(
        name='posting',
        endpoint='postings',
        id_field='id',
        label_field='title',
        allow_children_make_new=True,
        fields_list=[
            FieldTemplate(name='platform', type=FieldType.TEXT, is_required=True),
            FieldTemplate(name='company', type=FieldType.TEXT, is_required=True),
            FieldTemplate(name='title', type=FieldType.TEXT, is_required=True),
            FieldTemplate(name='salary', type=FieldType.NUMBER, is_required=False),
            FieldTemplate(name='description', type=FieldType.MULTILINE_TEXT, is_required=False),
            FieldTemplate(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=True),
            FieldTemplate(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=True),
            FieldTemplate(name='remote', type=FieldType.BOOLEAN, is_required=False),
        ],
    )

    ApplicationForm = Form(
        name='application',
        endpoint='applications',
        id_field='id',
        label_field='id',
        allow_children_make_new=True,
        fields_list=[
            FieldTemplate(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings'),
            FieldTemplate(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes'),
            FieldTemplate(name='date_submitted', type=FieldType.DATE, is_required=True),
        ],
    )

    ResponseTypeForm = Form(
        name='response_type',
        endpoint='response_types',
        id_field='id',
        label_field='id',
        allow_children_make_new=True,
        fields_list=[
            FieldTemplate(name='name', type=FieldType.TEXT, is_required=True)
        ],
    )

    ResponseForm = Form(
        name='response',
        endpoint='responses',
        id_field='id',
        label_field='id',
        allow_children_make_new=True,
        fields_list=[
            FieldTemplate(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications'),
            FieldTemplate(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types'),
            FieldTemplate(name='date_received', type=FieldType.DATE, is_required=True),
            FieldTemplate(name='data', type=FieldType.TEXT, is_required=False),
        ],
    )

    all_forms = [ResumeForm, PostingForm, ApplicationForm, ResponseTypeForm, ResponseForm]
    return all_forms


if __name__ == "__main__":
    # Initialize forms
    all_forms = create_forms()

    # Initialize api client, crud_form, table
    api_client = APIClient(base_url=api_url)
    crud_form = DynamicCRUDForm(api_client, all_forms)
    table_display = TableDisplay(api_client=api_client)   

    # Prepare forms for use
    crud_form.initialize_forms()

    # Maps human readable names to form endpoints
    form_endpoints = {form.endpoint.title().replace('_', ' '): form.endpoint for form in all_forms}

    # Sidebar for selecting entity
    with st.sidebar:
        st.header("Select Entity")
        selected_entity = st.radio(
            "Choose a table",
            form_endpoints
        )
    
    # Form endpoint currently selected
    endpoint = form_endpoints[selected_entity]

    with st.expander('Data'):
        table_display.show_table(endpoint)

    with st.expander('Form', expanded=True):
        crud_form.run(endpoint)
