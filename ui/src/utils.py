from src.api import APIClient
from src.components.form_tree import FormTree
import logging

logger = logging.getLogger(__name__)


# Factory function to create form instances
def create_form(api_client: APIClient, endpoint: str, all_forms: dict[str, type[FormTree]]):
    form_class = all_forms.get(endpoint)
    if not form_class:
        raise ValueError(f"No form class found for endpoint: {endpoint}")
    return form_class(api_client, all_forms=all_forms)
