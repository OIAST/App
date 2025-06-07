import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def run(symbol):
    st.subheader(f"📊 Volume Analysis for {symbol}")

    # 取得 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ No data found. Please check the stock symbol.")
        return

    # 計算 20 日均量與標準差
    data["Volume"] = data["Volume"].fillna(0).astype(int)
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 顯示表格（最後 30 天）
    display_data = data[["Volume", "volume_ma20", "volume_std20"]].copy()
    st.write("📋 Volume Statistics (Last 30 Days)")
    st.dataframe(display_data.tail(30))

    # 畫靜態折線圖
    st.write("📈 Volume Chart (with 20-day MA & STD)")
    fig, ax = plt.subplots(figsize=(10, 4))

    # 日期格式轉換
    data = data.tail(60)  # 顯示最近 60 天
    dates = data.index.strftime("%y/%m/%d")

    ax.plot(dates, data["volume_ma20"], label="20-Day MA", color="orange")
    ax.plot(dates, data["volume_std20"], label="20-Day STD", color="green", linestyle="--")
    ax.bar(dates, data["Volume"], label="Volume", color="skyblue", width=0.6)

    ax.set_title("Volume Analysis")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume")
    ax.legend()
    ax.grid(True)

    # X 軸字體縮小，避免擠壓
    ax.tick_params(axis='x', labelsize=8)
    fig.autofmt_xdate(rotation=45)

    st.pyplot(fig)