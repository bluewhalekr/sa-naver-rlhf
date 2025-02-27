import time
from datetime import timedelta
from typing import List

import streamlit as st

from config import PROMPT_API_URL
from logger import logger
from models import PromptGetResponse, PromptSetRequest, PromptSetResponse
from services.module import ApiClient


def request_get_prompt(question_type: str):
    username = st.session_state.get('username', 'unknown')
    logger.info(f"{username.rjust(12)}| request_get_prompt")

    api_client = ApiClient()
    json_response = api_client.get(PROMPT_API_URL+f'/{question_type}')

    return json_response


def get_prompt(question_type: str) -> str:
    json_response = request_get_prompt(question_type)
    response = PromptGetResponse(**json_response)

    return response.prompt


def request_set_prompt(question_type: str, req_data: dict):
    username = st.session_state.get('username', 'unknown')
    logger.info(f"{username.rjust(12)}| request_set_prompt")

    api_client = ApiClient()
    json_response = api_client.post(PROMPT_API_URL+f'/{question_type}', data=req_data)

    return json_response


def set_prompt(question_type: str, prompt: str):
    req_data = PromptSetRequest(prompt=prompt)
    request_set_prompt(question_type, req_data.dict())
