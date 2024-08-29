# ./src/app.py
import streamlit as st
from src.settings import api_url, layout_mode
from src.api import APIClient
from src.components.form import FormTree, init_form_tree
from src.schemas import FieldTemplate
import logging

logger = logging.getLogger(__name__)


class DynamicCRUDForm:
    def __init__(self, api_client: APIClient, forms: list[type[FormTree]] = []):
        self.api_client: APIClient = api_client
        self.forms: list[type[FormTree]] = forms
        self.form_endpoint_map: dict[str, type[FormTree]] = {}

    def initialize_forms(self):
        # Mapping form endpoint to form
        form_endpoint_map = {form.endpoint: form for form in self.forms}

        for form in self.forms:
            # Convert any FieldTemplates to the correct Field class
            form.fields_list = self._get_initialized_fields_from_form(form, form_endpoint_map)
            form_endpoint_map[form.endpoint] = form

        self.form_endpoint_map = form_endpoint_map

    def _get_initialized_fields_from_form(self, form: type[FormTree], form_endpoint_map):
        new_fields_list = []
        for field in form.fields_list:
            if not isinstance(field, FieldTemplate):
                new_fields_list.append(field)
            else:
                initialized_field = field.as_field(
                    form_name=form.name, 
                    form_endpoint=form.endpoint, 
                    forms=form_endpoint_map
                )
                new_fields_list.append(initialized_field)

        return new_fields_list

    def run(self, endpoint):
        with st.container(border=True):
            # Display selected table and forms
            st.header(f"{endpoint.capitalize().replace('_', ' ')}")
            init_form_tree(self.api_client, endpoint, self.form_endpoint_map).show_form()
