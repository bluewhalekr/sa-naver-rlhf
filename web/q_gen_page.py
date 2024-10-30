import json
import os
from datetime import timedelta
from typing import List

import httpx
import streamlit as st
from pydantic import BaseModel
from requests.exceptions import HTTPError

from logger import logger

# 데이터 가져올 수 있는 API의 url
API_URL = "https://task1.smart-agent.bluewhale.kr/v1/questions"

WEB_ROOT = os.path.dirname(__file__)
TOKEN_PATH = "/app/configs/token.json"
if not os.path.exists(TOKEN_PATH):
    TOKEN_PATH = os.path.join(WEB_ROOT, "web_configs", "token.json")

ASSET_ROOT = os.path.join(WEB_ROOT, 'assets')
ICON_PATH = os.path.join(ASSET_ROOT, "AIMMO-시그니처 로고_바이올렛+블랙.png")

BTN_WAITING_TIME = 10


class ImageInfo(BaseModel):
    keyword: str
    image_url: str


class ImageQuestions(BaseModel):
    image_info: List[ImageInfo]
    questions: List[str]


@st.cache_resource(ttl=timedelta(hours=1))
def get_httpx_client():
    transport = httpx.HTTPTransport(retries=3)
    client = httpx.Client(transport=transport)
    return client


httpx_client = get_httpx_client()


@st.cache_data(ttl=timedelta(minutes=1))
def open_image_url(image_url) -> bytes:
    logger.info(f"{st.session_state['username'].rjust(12)}| request image URL: {image_url}")

    try:
        response = httpx_client.get(image_url)

    except Exception as e:
        raise HTTPError(f"Failed to open image URL: {image_url}") from e

    if response.status_code == 200:
        return response.content

    else:
        raise HTTPError(f"[{response.status_code}] Failed to open image URL: {image_url}")


@st.cache_data(ttl=timedelta(seconds=BTN_WAITING_TIME-1), hash_funcs={int: lambda x: True})
def get_image_questions(user_id: str, image_num: int) -> dict:
    logger.info(f"{st.session_state['username'].rjust(12)}| request image questions. nums: {image_num}")

    headers = {
        "Authorization": f"Bearer {user_id}"
    }
    url_with_params = f"{API_URL}?image_count={image_num}"

    try:
        response = httpx_client.get(url_with_params, headers=headers)

    except Exception as e:
        raise HTTPError(f"Failed to get image questions, url: {url_with_params}") from e

    if response.status_code == 200:
        return response.json()

    else:
        raise HTTPError(f"[{response.status_code}] Failed to get image questions: {response.content}")


@st.cache_data
def get_user_token(username: str) -> str:
    with open(TOKEN_PATH, "r") as f:
        username_to_token = json.load(f)

    if token := username_to_token.get(username):
        return token

    else:
        raise ValueError("Please login first.")


@st.fragment
def radio_button():
    st.logo(ICON_PATH, icon_image=ICON_PATH)
    image_num = st.radio("이미지 개수", [1, 2, 3], horizontal=True)

    return image_num


@st.fragment
def btn_click_action(image_num):
    username = st.session_state['username']
    logger.info(f"{username.rjust(12)}| button clicked")

    token = get_user_token(username)

    with st.spinner("이미지와 질문을 가져오는 중..."):
        image_questions = get_image_questions(token, image_num)
        image_questions = ImageQuestions(**image_questions)
        image_num = len(image_questions.image_info)

        # Display images
        st.markdown("### 이미지")

        columns = st.columns(image_num, vertical_alignment="bottom")
        for image_col, image_info in zip(columns, image_questions.image_info):
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


def btn_click_callback():
    st.session_state.btn_clicked = True


def btn_init():
    st.session_state.btn_clicked = False


@st.fragment(run_every=BTN_WAITING_TIME)
def btn():
    btn_disabled = st.session_state.btn_clicked
    if st.button(
        "이미지 검색 및 질문 생성하기",
        use_container_width=True,
        disabled=btn_disabled,
        on_click=btn_click_callback,
    ):
        st.rerun()

    return st.session_state.btn_clicked


@st.fragment
def q_gen():
    image_num = radio_button()

    if btn():
        btn_click_action(image_num)
        btn_init()


def page_main():
    if not st.session_state.get('btn_clicked'):
        st.session_state['btn_clicked'] = False

    if st.session_state['authentication_status']:
        q_gen()

    else:
        st.warning("로그인이 필요합니다.")


page_main()
