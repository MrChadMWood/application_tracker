import streamlit as st
import pandas as pd
from datetime import datetime
from src.settings import logger, api_url, layout_mode
from src.api import APIClient
from src.components.table import TableDisplay
from src.components.forms import create_form

st.set_page_config(layout=layout_mode)


class StreamlitApp:
    def __init__(self):
        self.api_client = APIClient(base_url=api_url)
        self.table_display = TableDisplay(api_client=self.api_client)

    def run(self):
        # Define endpoints based on selected entity
        # Each endpoint cooresponds to a URI and CRUD form
        endpoints = {
            "Resumes": "resumes",
            "Postings": "postings",
            "Applications": "applications",
            "Response Types": "response_types",
            "Responses": "responses"
        }

        # Sidebar for selecting entity
        with st.sidebar:
            st.header("Select Entity")
            selected_entity = st.radio(
                "Choose a table",
                endpoints
            )

        endpoint = endpoints[selected_entity]

        # Display selected table and forms
        st.header(f"{endpoint.capitalize().replace('_', ' ')}")
        left_side, right_side = st.columns(2)

        with left_side:
            create_form(self.table_display.api_client, endpoint).show_form()
        
        with right_side:
            with st.expander("Display Data"):
                self.table_display.show_table(endpoint)

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
