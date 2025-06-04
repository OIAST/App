import streamlit as st
import yfinance as yf
import pandas as pd

def render_rsi_bar(symbol: str):
    st.subheader("📊 RSI 價格區間（簡化條狀圖）")

    # 取得股價資料
    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty:
        st.warning("無法取得股價資料")
        return

    close = data["Close"]
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    current_price = close.iloc[-1]
    current_rsi = rsi.iloc[-1]

    # 模擬 RSI 30 和 70 對應的價格（簡化法）
    low_rsi_price = round(current_price * (30 / current_rsi), 2) if not pd.isna(current_rsi) else current_price * 0.9
    high_rsi_price = round(current_price * (70 / current_rsi), 2) if not pd.isna(current_rsi) else current_price * 1.1

    # 計算目前價格在 RSI 區間的位置比例（0~1）
    try:
        price_position = (current_price - low_rsi_price) / (high_rsi_price - low_rsi_price)
        price_position = min(max(price_position, 0), 1)  # 限制在 [0,1]
    except ZeroDivisionError:
        price_position = 0.5

    # 顯示條狀圖
    st.markdown("**RSI 對應股價區間**")
    bar = "─" * int(price_position * 20) + "●" + "─" * (20 - int(price_position * 20))
    st.markdown(f"{30} (${low_rsi_price}) {bar} {70} (${high_rsi_price})")
    st.markdown(f"📌 **目前股價：${round(current_price,2)} | RSI：{round(current_rsi, 2)}**")