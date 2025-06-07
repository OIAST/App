import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def run(symbol):
    st.subheader(f"📊 Volume Analysis for {symbol}")

    # 抓取 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 計算 20 日均量與標準差
    data["Volume"] = data["Volume"].fillna(0).astype(int)
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 顯示表格（最近 30 天）
    display_data = data[["Volume", "volume_ma20", "volume_std20"]].copy()
    st.write("📋 Volume Statistics (Last 30 Days)")
    st.dataframe(display_data.tail(30))

    # 畫靜態折線圖（無柱狀圖）
    st.write("📈 Volume Chart (with 20-day MA & STD)")
    fig, ax = plt.subplots(figsize=(10, 4))

    recent_data = data.tail(60)
    dates = recent_data.index.strftime("%y/%m/%d")

    ax.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
    ax.plot(dates, recent_data["volume_ma20"], label="20-Day MA", color="orange")
    ax.plot(dates, recent_data["volume_std20"], label="20-Day STD", color="green", linestyle="--")

    ax.set_title("Volume Analysis")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume")
    ax.legend()
    ax.grid(True)

    # X 軸字體縮小並旋轉
    ax.tick_params(axis='x', labelsize=8)
    fig.autofmt_xdate(rotation=45)

    st.pyplot(fig)