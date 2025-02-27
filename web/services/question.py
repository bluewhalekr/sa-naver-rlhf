import time
from datetime import timedelta
from typing import List
from httpx import HTTPStatusError

import streamlit as st

from config import QUESTION_API_URL, TEST_MODE
from logger import logger
from models import ImageUrlInfo, ImageQuestion, ImageQuestionsRequestData, ImageQuestionsResponse
from services.module import ApiClient

MOCK_QUESTIONS = {
    "questions": [
        {
            'question': '겨울엔 어디로 여행가는 게 좋을까?',
            'image_keywords': ['북한산', '제주도']
        },
        {
            'question': '여행가서 뭐하지?',
        },
        {
            'question': '여행가서 즐기기 좋은 레크레이션은?',
        },
        {
            'question': '혼자 여행 가면 심심할까?',
        },
        {
            'question': '여행에 꼭 챙겨할 물품은?',
        },
        {
            'question': '더 있을까?',
        },
        {
            'question': '여행 전에 체크해야할 것들은?',
        },
        {
            'question': '여행 재밌겠지?',
        },
        {
            'question': '여기 어디인지 추측해봐',
            'image_keywords': ['북한산']
        },
        {
            'question': '제주도에서 할 수 있는 액티비티는?',
        }
    ]
}


def hash_func(d):
    keywords = [image_url_info['keyword'].replace(' ', '') for image_url_info in d['choices']]
    keywords.sort()
    hash_str = f"{d['username']}:{d['question_type']}:{','.join(keywords)}"
    return hash_str


@st.cache_data(ttl=timedelta(seconds=10), show_spinner=False)
def request_questions(req_data: dict):
    username = st.session_state.get('username', 'unknown')
    logger.info(f"{username.rjust(12)}| request_questions")

    if TEST_MODE:
        time.sleep(1)
        json_response = MOCK_QUESTIONS

    else:
        api_client = ApiClient()
        try:
            json_response = api_client.post(QUESTION_API_URL, data=req_data)
        except HTTPStatusError as e:
            if e.response.status_code == 500 and 'GptAssistantResponseError' in e.response.content.decode():
                logger.error("No available persona image info")
                return None
            else:
                raise e

    return json_response


def get_questions(persona: str, choices: List[ImageUrlInfo], prompt: str, username: str) -> List[ImageQuestion]:
    keyword_to_image_url = {choice.keyword: choice.image_url for choice in choices}

    req_data = ImageQuestionsRequestData(user_id=username, persona=persona, choices=choices, prompt=prompt)
    if json_response := request_questions(req_data.dict()):
        response = ImageQuestionsResponse(**json_response)

        return response.questions

    return []
