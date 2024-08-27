# ./src/app.py
import streamlit as st
from src.settings import api_url, layout_mode
from src.api import APIClient
from src.components.table import TableDisplay
from src.components.form import FormTree, init_form_tree
import logging

logger = logging.getLogger(__name__)


class CRUDApp:
    def __init__(self, api_client: APIClient, endpoints: dict[str, str], all_forms: dict[str, type[FormTree]]):
        self.api_client: APIClient = api_client
        self.table_display: TableDisplay = TableDisplay(api_client=api_client)
        self.form_endpoints: dict[str, str] = endpoints
        self.all_forms: dict[str, type[FormTree]] = all_forms

    def run(self):
        # Sidebar for selecting entity
        with st.sidebar:
            st.header("Select Entity")
            selected_entity = st.radio(
                "Choose a table",
                self.form_endpoints
            )
            
        endpoint = self.form_endpoints[selected_entity]

        # Display selected table and forms
        st.header(f"{endpoint.capitalize().replace('_', ' ')}")
        left_side, right_side = st.columns(2)

        with left_side:
            init_form_tree(self.api_client, endpoint, self.all_forms).show_form()
        
        with right_side:
            with st.expander("Display Data"):
                self.table_display.show_table(endpoint)
