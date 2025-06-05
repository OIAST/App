import streamlit as st

# ✅ 初始化 session 狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False
if "username" not in st.session_state:
    st.session_state.username = ""

from login import login, logout
from ui import render_floating_price_box
from analysis import chips, fundamental, technical, probability

import yfinance as yf  # ✅ 移到這裡避免重複載入

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
    elif analysis_type == "技術面":
        data = yf.download(symbol, period="3mo", interval="1d")

        # ✅ 防呆：確保 Volume 存在且不全為 NaN
        if "Volume" not in data.columns or data["Volume"].dropna().empty:
            st.error("⚠️ 無法取得有效的 Volume 資料，請確認該股票是否支援交易量分析。")
        else:
            technical.run(symbol, data)
    elif analysis_type == "股價機率分析":
        probability.run(symbol)