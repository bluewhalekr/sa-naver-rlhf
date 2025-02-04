import streamlit as st
from config import ICON_PATH
from logger import logger

from services.auth import authenticate


def login_view():
    st.logo(ICON_PATH, icon_image=ICON_PATH)

    login_form = st.form(key="login_form")
    login_form.subheader('Login')
    username = login_form.text_input('Username')
    token = login_form.text_input('Password', type='password')

    if login_form.form_submit_button('Login'):
        if not username or not token:
            st.warning("username or password is empty")

        elif authenticate(username, token):
            st.session_state['authentication_status'] = True
            st.session_state['username'] = username
            st.session_state['token'] = token
            logger.info(f"{st.session_state['username'].rjust(12)}| user authenticated")

        else:
            st.warning("wrong username or password")

    if st.session_state.get('authentication_status'):
        st.rerun()


def logout_view():
    st.logo(ICON_PATH, icon_image=ICON_PATH)
    st.session_state['authentication_status'] = False
    st.session_state['username'] = ''
    st.session_state['token'] = ''
    logger.info(f"{st.session_state['username'].rjust(12)}| user logged out")

    st.rerun()
