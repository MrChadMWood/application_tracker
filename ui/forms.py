# ./src/forms.py
from src.schemas import Field, ForeignKeyField, FieldType
from src.components.form_tree import FormTree

# Define specific forms for each endpoint
class ResumeForm(FormTree):
    name = 'resumes'
    endpoint = 'resumes'
    fields_list = [
        Field(name='data', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint)
    ]

    def __init__(self, api_client, all_forms):
        super().__init__(api_client, self.fields_list, forms=all_forms)

class PostingForm(FormTree):
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

    def __init__(self, api_client, all_forms):
        super().__init__(api_client, self.fields_list, forms=all_forms)

class ApplicationForm(FormTree):
    name = 'application'
    endpoint = 'applications'
    fields_list = [
        ForeignKeyField(name='posting_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='postings', parent_id='id', parent_label='title', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        ForeignKeyField(name='resume_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='resumes', parent_id='id', parent_label='data', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='date_submitted', type=FieldType.DATE, is_required=True, form_name=name, form_endpoint=endpoint),
    ]

    def __init__(self, api_client, all_forms):
        super().__init__(api_client, self.fields_list, forms=all_forms)

class ResponseTypeForm(FormTree):
    name = 'response_type'
    endpoint = 'response_types'
    fields_list = [
        Field(name='name', type=FieldType.TEXT, is_required=True, form_name=name, form_endpoint=endpoint)
    ]

    def __init__(self, api_client, all_forms):
        super().__init__(api_client, self.fields_list, forms=all_forms)

class ResponseForm(FormTree):
    name = 'response'
    endpoint = 'responses'
    fields_list = [
        ForeignKeyField(name='application_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='applications', parent_id='id', parent_label='id', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        ForeignKeyField(name='response_type_id', type=FieldType.FOREIGN_KEY, is_required=True, parent_endpoint='response_types', parent_id='id', parent_label='name', parent_allow_new=True, form_name=name, form_endpoint=endpoint),
        Field(name='date_received', type=FieldType.DATE, is_required=True, form_name=name, form_endpoint=endpoint),
        Field(name='data', type=FieldType.TEXT, is_required=False, form_name=name, form_endpoint=endpoint),
    ]

    def __init__(self, api_client, all_forms):
        super().__init__(api_client, self.fields_list, forms=all_forms)


# All forms, fed back to FormTree 
# for use with foreign key fields
# Maps endpoints to forms
all_forms = {
    "resumes": ResumeForm,
    "postings": PostingForm,
    "applications": ApplicationForm,
    "response_types": ResponseTypeForm,
    "responses": ResponseForm
}

# Maps endpoint labels to endpoints
endpoints = {
    "Resumes": "resumes",
    "Postings": "postings",
    "Applications": "applications",
    "Response Types": "response_types",
    "Responses": "responses"
}
