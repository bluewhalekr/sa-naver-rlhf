import streamlit as st

from logger import logger
from services.image_url import get_persona_image_infos
from services.question import get_questions
from streamlit_utils import image_show, lazy_button, logo_fragment


@st.fragment
def question_type_checkbox():
    logo_fragment()

    question_type = st.radio("질문 유형", ["SM", "MS", "MM-1", "MM-2"], horizontal=True)
    return question_type


@st.fragment
def questions_view(choices, question_type):
    username = st.session_state['username']
    persona = st.session_state['persona']
    with st.spinner("질문을 가져오는 중..."):
        questions = get_questions(persona, choices, question_type, username)

    for image_question in questions:
        with st.chat_message("user"):
            col1, col2 = st.columns([1, 1], border=False, vertical_alignment="top", gap="small")
            with col1:
                st.code(image_question.question)

            with col2:
                if image_question.image_infos:
                    with st.container(border=True):
                        columns = st.columns(5, vertical_alignment="bottom")
                        for col, ref_image_info in zip(columns, image_question.image_infos):
                            col.image(ref_image_info.image_url)
                            col.code(ref_image_info.keyword)
                            col.code(ref_image_info.image_url)


def image_checkbox_view(image_urls):
    image_num = len(image_urls)

    choices = []
    with st.spinner("이미지와 질문을 가져오는 중..."):
        columns = st.columns(image_num, vertical_alignment="bottom")
        for col_idx, (image_col, (keyword, image_url)) in enumerate(zip(columns, image_urls)):
            image_col.image(image_url)
            if image_col.checkbox(keyword, key=col_idx):
                choices.append((keyword, image_url))


@st.fragment
def image_choice_view(image_url_infos):
    username = st.session_state['username']
    image_num = len(image_url_infos)

    choices = []
    with st.spinner("이미지와 질문을 가져오는 중..."):
        columns = st.columns(image_num, vertical_alignment="bottom")
        for col_idx, (image_col, image_url_info) in enumerate(zip(columns, image_url_infos)):
            with image_col:
                image_show(image_url_info.image_url)
                if image_col.checkbox(image_url_info.keyword, key=col_idx):
                    choices.append(image_url_info)

    if 3 <= len(choices) <= 5:
        question_type = question_type_checkbox()

        if st.button("질문 생성하기", use_container_width=True):
            logger.info(f"{username.rjust(12)}| question button clicked")
            questions_view(choices, question_type)

    else:
        st.info("3개 이상 5개 이하의 이미지를 선택해주세요.")


@st.fragment
def image_button_click_action():
    logo_fragment()

    username = st.session_state['username']
    persona_image_infos = get_persona_image_infos(username)
    st.session_state['persona'] = persona_image_infos.persona
    image_choice_view(persona_image_infos.image_infos)


def serve_view():
    if st.session_state.get('authentication_status'):
        if lazy_button("image", "이미지 검색 및 질문 생성하기"):
            username = st.session_state['username']
            logger.info(f"{username.rjust(12)}| image button clicked")
            image_button_click_action()

    else:
        st.warning("로그인이 필요합니다.")
