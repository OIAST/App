import streamlit as st
import bcrypt

username_correct = "david"
hashed_password = b"$2b$12$vSeJMa5mUnyvdyFyI8BBKutgLW8QSdEc5uj7ABm5y3Z/W6UesojXC"  # 密碼1234

def login():
    def handle_login():
        username = st.session_state.username_input
        password = st.session_state.password_input
        if username == username_correct and bcrypt.checkpw(password.encode(), hashed_password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_error = False
            st.experimental_rerun()
        else:
            st.session_state.login_error = True

    st.title("🔐 請先登入")
    with st.form("login_form"):
        st.text_input("帳號", key="username_input")
        st.text_input("密碼", type="password", key="password_input")
        st.form_submit_button("登入", on_click=handle_login)

    if st.session_state.login_error:
        st.error("❌ 帳號或密碼錯誤")

def logout():
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()