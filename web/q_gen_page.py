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
API_URL = "https://task1.smart-agent.bluewhale.kr/v2/questions"

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


class ImageQuery(BaseModel):
    query: str
    image_infos: List[ImageInfo]


class ImageQueries(BaseModel):
    intent_id: int
    image_queries: List[ImageQuery]


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
def get_image_questions(user_id: str) -> dict:
    logger.info(f"{st.session_state['username'].rjust(12)}")

    headers = {
        "Authorization": f"Bearer {user_id}"
    }
    url_with_params = f"{API_URL}"

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
def btn_click_action():
    username = st.session_state['username']
    logger.info(f"{username.rjust(12)}| button clicked")

    token = get_user_token(username)

    with st.spinner("이미지와 질문을 가져오는 중..."):
        image_queries = get_image_questions(token)
        image_queries = ImageQueries(**image_queries).image_queries

        tab_labels = [str(q_i+1) for q_i in range(len(image_queries))]
        tabs = st.tabs(tab_labels)
        for tab, image_query in zip(tabs, image_queries):
            columns = tab.columns(3, vertical_alignment="bottom")
            for image_col, image_info in zip(columns, image_query.image_infos):
                image_data = open_image_url(image_info.image_url)

                image_col.image(image_data)

                image_col.json(image_info.model_dump())

            query = image_query.query
            with tab.chat_message("user"):
                st.code(query, language="html")


def btn_click_callback():
    st.session_state.btn_clicked = True


def btn_init():
    st.session_state.btn_clicked = False


@st.fragment(run_every=BTN_WAITING_TIME)
def btn():
    st.logo(ICON_PATH, icon_image=ICON_PATH)  # radio 버튼 action이 실행될 때마다 로고가 사라지는 이슈 => logo 함수 여기에 위치
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
    if btn():
        btn_click_action()
        btn_init()


def page_main():
    if not st.session_state.get('btn_clicked'):
        st.session_state['btn_clicked'] = False

    if st.session_state['authentication_status']:
        q_gen()

    else:
        st.warning("로그인이 필요합니다.")


page_main()
