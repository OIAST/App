import streamlit as st

# ✅ Session 初始化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False
if "username" not in st.session_state:
    st.session_state.username = ""

from login import login, logout
from ui import render_floating_price_box
from analysis import chips, fundamental, technical, probability

# 頁面設定
st.set_page_config(layout="wide")

# 登入流程
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.success(f"👋 歡迎 {st.session_state.username}")
    logout()

    st.title("📈 美股分析工具")
    symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()
    analysis_type = st.selectbox("選擇分析項目", ["基本面", "籌碼面", "技術面", "股價機率分析"])

    render_floating_price_box(symbol)

    if analysis_type == "籌碼面":
        chips.run(symbol)
    elif analysis_type == "基本面":
        fundamental.run(symbol)
    elif analysis_type == "股價機率分析":
        probability.run(symbol)



## elif analysis_type == "技術面":
       ## technical.run(symbol)