import streamlit as st

from logger import logger
from views.auth import login_view, logout_view
from views.serve import serve_view

st.set_page_config(page_title="Question Gen", page_icon="🤖", layout="wide")


def init_session():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False

    if 'username' not in st.session_state:
        st.session_state['username'] = ''

    if 'token' not in st.session_state:
        st.session_state['token'] = ''


def main():
    init_session()

    # Page definitions
    login_page = st.Page(login_view, title="Log in", icon=":material/login:")
    logout_page = st.Page(logout_view, title="Log out", icon=":material/logout:")
    serve_page = st.Page(serve_view, title="질문 생성", icon=":material/chat:")

    # Page routing
    if st.session_state['authentication_status']:
        page_dict = {"Question": [serve_page], "Account": [logout_page]}
        pg = st.navigation(page_dict)

    else:
        pg = st.navigation([login_page])

    pg.run()


try:
    main()

except Exception as e:
    st.error(f"에러가 발생했습니다. 매니저 또는 개발자에게 문의해주세요. {e.__class__.__name__}")
    logger.exception(e)
