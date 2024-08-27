import streamlit as st
import logging
from src.settings import api_url, layout_mode
from src.api import APIClient
from src.app import CRUDApp

logger = logging.getLogger(__name__)
st.set_page_config(layout=layout_mode)


from src.schemas import Field, ForeignKeyField, FieldType
from src.components.form import Form, FormTree
from src.api import APIClient


def create_forms():
    ResumeForm = Form(
        name='resumes',
        endpoint='resumes',
        fields_list=[
            Field(name='data', type=FieldType.TEXT, is_required=True, form_name='resumes', form_endpoint='resumes')
        ],
    )

    PostingForm = Form(
        name='posting',
        endpoint='postings',
        fields_list=[
            Field(name='platform', type=FieldType.TEXT, is_required=True, form_name='posting', form_endpoint='postings'),
            Field(name='company', type=FieldType.TEXT, is_required=True, form_name='posting', form_endpoint='postings'),
            Field(name='title', type=FieldType.TEXT, is_required=True, form_name='posting', form_endpoint='postings'),
            Field(name='salary', type=FieldType.NUMBER, is_required=False, form_name='posting', form_endpoint='postings'),
            Field(name='description', type=FieldType.MULTILINE_TEXT, is_required=False, form_name='posting', form_endpoint='postings'),
            Field(name='responsibilities', type=FieldType.MULTILINE_TEXT, is_required=True, form_name='posting', form_endpoint='postings'),
            Field(name='qualifications', type=FieldType.MULTILINE_TEXT, is_required=True, form_name='posting', form_endpoint='postings'),
            Field(name='remote', type=FieldType.BOOLEAN, is_required=False, form_name='posting', form_endpoint='postings'),
        ],
    )

    ApplicationForm = Form(
        name='application',
        endpoint='applications',
        fields_list=[
            ForeignKeyField(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name='application', form_endpoint='applications'),
            ForeignKeyField(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name='application', form_endpoint='applications'),
            Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name='application', form_endpoint='applications'),
        ],
    )

    ResponseTypeForm = Form(
        name='response_type',
        endpoint='response_types',
        fields_list=[
            Field(name='name', type=FieldType.TEXT, is_required=True, form_name='response_type', form_endpoint='response_types')
        ],
    )

    ResponseForm = Form(
        name='response',
        endpoint='responses',
        fields_list=[
            ForeignKeyField(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', parent_allow_new=True, form_name='response', form_endpoint='responses'),
            ForeignKeyField(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', parent_allow_new=True, form_name='response', form_endpoint='responses'),
            Field(name='date_received', type=FieldType.DATE, is_required=True, form_name='response', form_endpoint='responses'),
            Field(name='data', type=FieldType.TEXT, is_required=False, form_name='response', form_endpoint='responses'),
        ],
    )

    return {
        "resumes": ResumeForm,
        "postings": PostingForm,
        "applications": ApplicationForm,
        "response_types": ResponseTypeForm,
        "responses": ResponseForm
    }


if __name__ == "__main__":
    all_forms = create_forms()
    endpoints = {k.title().replace('_', ' '): k for k in all_forms}

    api_client = APIClient(base_url=api_url)
    app = CRUDApp(api_client, endpoints, all_forms)
    app.run()
