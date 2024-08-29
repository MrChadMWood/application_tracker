# ./src/components/form.py
import streamlit as st
from src.components.form_tree import FormTree
from src.api import APIClient
import logging

logger = logging.getLogger(__name__)


class Form(FormTree):
    def __init__(self, name, endpoint, fields_list, id_field, label_field, allow_children_make_new):
        self.name = name
        self.endpoint = endpoint
        self.fields_list = fields_list
        self.id_field = id_field
        self.label_field = label_field
        self.allow_children_make_new = allow_children_make_new

    def init_tree(self, api_client, all_forms):
        # Passes all forms so FormTree can lookup child fields during FK propagation
        super().__init__(api_client, self.fields_list, forms=all_forms)
        return self

def init_form_tree(api_client: APIClient, endpoint: str, all_forms: dict[str, type[Form]]):
    form_class = all_forms.get(endpoint)
    if not form_class:
        raise ValueError(f"No form class found for endpoint: {endpoint}")
    return form_class.init_tree(api_client=api_client, all_forms=all_forms)
