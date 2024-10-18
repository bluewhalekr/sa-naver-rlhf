import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
AUTH_CONFIG_PATH = os.path.join(WEB_ROOT, 'web_configs', 'auth.yaml')
st.set_page_config(page_title="Question Gen", page_icon="🤖", layout="wide")


with open(AUTH_CONFIG_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

authenticator.login(location="unrendered")


def login():
    if not st.session_state['authentication_status']:
        authenticator.login()


def logout():
    if st.session_state['authentication_status']:
        authenticator.authentication_controller.logout()
        authenticator.cookie_controller.delete_cookie()


def register_user():
    if st.session_state['authentication_status'] and st.session_state['username'] == 'admin':
        authenticator.register_user()


# Page definitions
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

register_user_page = st.Page(register_user, title="Register user", icon=":material/security:")

q_gen_page = st.Page("question/generator.py", title="Question maker", icon=":material/chat:")

# Page routing
if st.session_state['authentication_status']:
    page_dict = {"Question": [q_gen_page]}

    if st.session_state['username'] == 'admin':
        page_dict["Admin"] = [register_user_page]

    page_dict["Account"] = [logout_page]
    pg = st.navigation(page_dict)

else:
    pg = st.navigation([st.Page(login, title="Log in", icon=":material/login:")])

pg.run()

