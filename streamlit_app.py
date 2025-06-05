import streamlit as st
import yfinance as yf

# ✅ 初始化 session 狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ✅ 匯入自訂模組
from login import login, logout
from ui import render_floating_price_box
from analysis import chips, fundamental, technical, probability

# ✅ 頁面設定
st.set_page_config(layout="wide", page_title="美股分析工具")

# ✅ 登入邏輯
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.success(f"👋 歡迎 {st.session_state.username}")
    logout()

    # ✅ 主介面內容
    st.title("📈 美股分析工具")
    symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()
    analysis_type = st.selectbox("選擇分析項目", ["基本面", "籌碼面", "技術面", "股價機率分析"])

    if symbol:
        render_floating_price_box(symbol)

        if analysis_type == "基本面":
            fundamental.run(symbol)
        elif analysis_type == "籌碼面":
            chips.run(symbol)
        elif analysis_type == "技術面":
            data = yf.download(symbol, period="3mo", interval="1d")
            technical.run(symbol, data)  # ✅ 改成傳入 data
        elif analysis_type == "股價機率分析":
            probability.run(symbol)
    else:
        st.info("請輸入股票代碼")