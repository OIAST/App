import streamlit as st

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_error" not in st.session_state:
        st.session_state.login_error = False
    if "username" not in st.session_state:
        st.session_state.username = ""
