import streamlit as st
import logging
from src.settings import api_url, layout_mode
from src.schemas import Field, ForeignKeyField, FieldType, FieldTemplate
from src.components.form import Form, FormTree
from src.api import APIClient
from src.app import CRUDApp

logger = logging.getLogger(__name__)
st.set_page_config(layout=layout_mode)

# Assigned a value due to streamlit magic otherwise embedding string into webapp.
todo = '''
TODO:
    A recent change updated Form class to include `id_field` as an attribute. Older code assumed that `"id"` was the id_field on a db table belonging to a form.
    As a result of this change, older code should be updated to reference the `id_field` attribute. Any reference to form labels should similarly utilize the `label_field` attribute.
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

    all_forms = {
        "resumes": ResumeForm,
        "postings": PostingForm,
        "applications": ApplicationForm,
        "response_types": ResponseTypeForm,
        "responses": ResponseForm
    }

    # Initializes all fields, using all_forms to inject metadata about foreign-keys
    for endpoint, form in all_forms.items():
        all_forms[endpoint] = form.convert_template_fields(all_forms)

    return all_forms


if __name__ == "__main__":
    # Initialize forms
    all_forms = create_forms()

    # Maps human readable names to form endpoints
    endpoints = {k.title().replace('_', ' '): k for k in all_forms}

    # Initialize api client, app, and run
    api_client = APIClient(base_url=api_url)
    app = CRUDApp(api_client, endpoints, all_forms)
    app.run()
