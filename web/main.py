import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
AUTH_CONFIG_PATH = '/app/configs/auth.yaml'
if not os.path.exists(AUTH_CONFIG_PATH):
    AUTH_CONFIG_PATH = os.path.join(WEB_ROOT, 'web_configs', 'auth.yaml')


st.set_page_config(page_title="Question Gen", page_icon="🤖", layout="wide")

IMAGE_ROOT = os.path.join(WEB_ROOT, 'images')
ICON_PATH = os.path.join(IMAGE_ROOT, "AIMMO-시그니처 로고_바이올렛+블랙.png")


with open(AUTH_CONFIG_PATH, 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

authenticator.login(location="unrendered")


def login():
    st.logo(ICON_PATH, icon_image=ICON_PATH)
    if st.session_state['authentication_status'] is None:
        authenticator.login()

    elif not st.session_state['authentication_status']:
        authenticator.login()
        st.warning("wrong username or password")


def logout():
    st.logo(ICON_PATH, icon_image=ICON_PATH)
    if st.session_state['authentication_status']:
        authenticator.authentication_controller.logout()
        authenticator.cookie_controller.delete_cookie()


# Page definitions
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

q_gen_page = st.Page("question/generator.py", title="질문 생성", icon=":material/chat:")

# Page routing
if st.session_state['authentication_status']:
    page_dict = {"Question": [q_gen_page], "Account": [logout_page]}
    pg = st.navigation(page_dict)

else:
    pg = st.navigation([st.Page(login, title="Log in", icon=":material/login:")])

pg.run()

