""" Custom Streamlit utility functions """

import streamlit as st

from config import BTN_WAITING_TIME, ICON_PATH


@st.cache_data
def image_show(image_url):
    st.image(image_url)


@st.fragment
def logo_fragment():
    st.logo(ICON_PATH, icon_image=ICON_PATH)  # radio 버튼 action이 실행될 때마다 로고가 사라지는 이슈 => logo 함수 여기에 위치


@st.fragment(run_every=BTN_WAITING_TIME)
def lazy_button(key: str, button_label: str, use_container_width: bool = True):
    logo_fragment()

    button_state_key = f"{key}_button_clicked"

    if not st.session_state.get(button_state_key):
        st.session_state[button_state_key] = False

    def button_click_callback():
        st.session_state[button_state_key] = True

    button_disabled = st.session_state[button_state_key]
    if st.button(
        button_label,
        use_container_width=use_container_width,
        disabled=button_disabled,
        on_click=button_click_callback,
    ):
        st.rerun()

    if st.session_state[button_state_key]:
        st.session_state[button_state_key] = False
        return True

    else:
        return False
