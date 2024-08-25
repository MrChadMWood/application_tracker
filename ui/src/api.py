import streamlit as st
import requests
from src.settings import logger


class HTTPError(Exception):
    pass

class JSONSerializeError(Exception):
    pass

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    @st.cache_data
    def fetch_data(_self, endpoint):
        logger.info(f'fetching: {_self.base_url}/{endpoint}')
        response = requests.get(f"{_self.base_url}/{endpoint}")
        return response.json()

    @st.cache_data
    def perform_crud(_self, endpoint, method, data=None, id=None):
        url = f"{_self.base_url}/{endpoint}" if not id else f"{_self.base_url}/{endpoint}/{id}"

        try:
            response = requests.request(method, url, json=data)
        except TypeError as e:
            raise JSONSerializeError(e)

        if not 200 <= response.status_code <= 299:
            raise HTTPError(f'{response.content}')

        return response.json()

    def clear_cache(self):
        self.fetch_data.clear()
        self.perform_crud.clear()