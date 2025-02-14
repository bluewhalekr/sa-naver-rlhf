from datetime import timedelta

import httpx
import streamlit as st

from logger import logger

CLIENT_LIFETIME = timedelta(hours=1)


@st.cache_resource(ttl=CLIENT_LIFETIME)
def get_httpx_client():
    transport = httpx.HTTPTransport(retries=3)
    client = httpx.Client(transport=transport)
    return client


class ApiClient:
    def __init__(self):
        self.client = get_httpx_client()

    def get(self, url, params=None):
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def post(self, url, data=None):
        try:
            response = self.client.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def put(self, url, data=None):
        try:
            response = self.client.put(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"An error occurred: {e}")
            raise e