"""Github integration."""
from django.conf import settings
import requests


class GhRequest:
    """Handle requests to github's API."""

    personal_token = settings.GH_PERSONAL_TOKEN
    headers = {
        "Authorization": f"token {personal_token}"
    }

    def __init__(self):
        """Init method."""
        print(self.personal_token)
        if not self.personal_token:
            raise ValueError("GH token not found")

    def post(self, url, graphql_query):
        "Handle GET requests toward Github's API"

        response = requests.post(
            url=url,
            headers=self.headers,
            json=graphql_query
        )
        return response.json()
