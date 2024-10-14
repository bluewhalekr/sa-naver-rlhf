import random

import httpx
import streamlit as st

from mocks import _tmp_get_image_questions
from model import ImageQuestions

st.set_page_config(page_title="Question Gen", page_icon="🤖", layout="wide")


def open_image_url(image_url) -> bytes:
    response = httpx.get(image_url)

    return response.content


def get_image_questions(img_num: int) -> ImageQuestions:
    if 1 <= img_num <= 3:
        return _tmp_get_image_questions(img_num)

    else:
        raise ValueError("Invalid image number")


image_num = st.radio("이미지 개수를 선택하세요", ["random", 1, 2, 3], horizontal=True)

if st.button("질문 생성"):
    if image_num == "random":
        image_num = random.randint(1, 3)

    if image_num:
        image_questions = get_image_questions(image_num)

        # Display images
        st.markdown("---")
        st.markdown("### 이미지")

        for image_col, image_info in zip(st.columns(image_num, vertical_alignment="bottom"), image_questions.image_infos):
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
