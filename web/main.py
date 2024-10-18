import os
import random

import httpx
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from mocks import _tmp_get_image_questions

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
AUTH_CONFIG_PATH = os.path.join(WEB_ROOT, 'web_configs', 'auth.yaml')
st.set_page_config(page_title="Question Gen", page_icon="🤖", layout="wide")


def open_image_url(image_url) -> bytes:
    response = httpx.get(image_url)

    return response.content


def get_image_questions(img_num: int):
    if 1 <= img_num <= 3:
        return _tmp_get_image_questions(img_num)

    else:
        raise ValueError("Invalid image number")


with open(AUTH_CONFIG_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

sb = st.sidebar
with sb:
    authenticator.login()

authentication_status = st.session_state['authentication_status']
if authentication_status:
    with sb:
        authenticator.logout()

    image_num = st.radio("이미지 개수를 선택하세요", ["random", 1, 2, 3], horizontal=True)

    if st.button("질문 생성"):
        if image_num == "random":
            image_num = random.randint(1, 3)

        if image_num:
            image_questions = get_image_questions(image_num)

            # Display images
            st.markdown("---")
            st.markdown("### 이미지")

            for image_col, image_info in zip(st.columns(image_num, vertical_alignment="bottom"),
                                             image_questions.image_infos):
                image_data = open_image_url(image_info.image_url)

                image_col.image(image_data)

                image_col.write("이미지 URL:")
                image_col.code(image_info.image_url, language="html")

                image_col.write("검색어:")
                image_col.code(image_info.search_word, language="html")

            # Display questions
            st.markdown("---")
            st.markdown("### 질문")

            for question in image_questions.questions:
                with st.chat_message("user"):
                    st.code(question, language="html")

elif authentication_status is False:
    st.error('Username/password is incorrect')

elif authentication_status is None:
    st.warning('Please enter your username and password')
