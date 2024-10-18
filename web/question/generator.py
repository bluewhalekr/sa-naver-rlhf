import logging
from datetime import timedelta
from typing import List

import httpx
import streamlit as st
from pydantic import BaseModel


# 데이터 가져올 수 있는 API의 url
API_URL = "https://task1.smart-agent.bluewhale.kr/v1/questions"
TEST_TOKEN = "smartagent160321!!"


class ImageInfo(BaseModel):
    keyword: str
    image_url: str


class ImageQuestions(BaseModel):
    image_info: List[ImageInfo]
    questions: List[str]


transport = httpx.HTTPTransport(retries=3)
client = httpx.Client(transport=transport)


@st.cache_data(ttl=timedelta(minutes=1))
def open_image_url(image_url) -> bytes:
    try:
        response = client.get(image_url)

    except Exception as e:
        raise ValueError(f"Failed to open image URL: {image_url}") from e

    if response.status_code == 200:
        return response.content

    else:
        raise ValueError(f"Failed to open image URL: {image_url}")


@st.cache_data(ttl=timedelta(seconds=10))
def get_image_questions(user_id: str) -> dict:
    headers = {
        "Authorization": f"Bearer {user_id}"
    }

    try:
        response = client.get(API_URL, headers=headers)

    except Exception as e:
        raise ValueError("Failed to get image questions") from e

    if response.status_code == 200:
        return response.json()

    else:
        raise ValueError("Failed to get image questions")


def get_user_token(email: str) -> str:
    return NotImplementedError


@st.fragment
def q_gen():
    if st.button("질문 생성", use_container_width=True):
        username = st.session_state['username']
        email = st.session_state['email']
        logging.debug(f"button clicked: {username}, {email}")

        if username == "admin":
            token = TEST_TOKEN
        else:
            token = get_user_token(email)

        image_questions = get_image_questions(token)
        image_questions = ImageQuestions(**image_questions)
        image_num = len(image_questions.image_info)

        # Display images
        st.markdown("---")
        st.markdown("### 이미지")

        for image_col, image_info in zip(st.columns(image_num, vertical_alignment="bottom"),
                                         image_questions.image_info):
            image_data = open_image_url(image_info.image_url)

            image_col.image(image_data)

            image_col.write("이미지 URL:")
            image_col.code(image_info.image_url, language="html")

            image_col.write("검색어:")
            image_col.code(image_info.keyword, language="html")

        # Display questions
        st.markdown("---")
        st.markdown("### 질문")

        col1, col2 = st.columns(2)
        for i, question in enumerate(image_questions.questions):
            col = col1 if i % 2 == 0 else col2
            with col:
                with st.chat_message("user"):
                    st.code(question, language="html")


if st.session_state['authentication_status']:
    q_gen()

else:
    st.warning("로그인이 필요합니다.")

