import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 主程式
def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20 日平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算變動率（今日與昨日差的比率）
    data["volume_ma20_change"] = data["volume_ma20"].pct_change()
    data["volume_std20_change"] = data["volume_std20"].pct_change()

    # 篩選最近 30 筆資料
    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%y/%m/%d")

    # 成交量與 MA 折線圖
    st.write("📈 Volume & MA20")
    fig1, ax1 = plt.subplots(figsize=(10, 3))
    ax1.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
    ax1.plot(dates, recent_data["volume_ma20"], label="20-Day MA", color="orange")
    ax1.set_title("Volume and 20-Day Moving Average")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Volume")
    ax1.tick_params(axis='x', labelsize=8)
    ax1.legend()
    ax1.grid(True)
    fig1.autofmt_xdate(rotation=45)
    st.pyplot(fig1)

    # 標準差變動率圖
    st.write("📉 20-Day STD Change Rate")
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.plot(dates, recent_data["volume_std20_change"], color="purple", label="STD Change Rate")
    ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax2.set_title("20-Day STD Change Rate")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Change Rate")
    ax2.tick_params(axis='x', labelsize=8)
    ax2.grid(True)
    ax2.legend()
    fig2.autofmt_xdate(rotation=45)
    st.pyplot(fig2)

    # 平均值變動率圖
    st.write("📉 20-Day MA Change Rate")
    fig3, ax3 = plt.subplots(figsize=(10, 3))
    ax3.plot(dates, recent_data["volume_ma20_change"], color="green", label="MA Change Rate")
    ax3.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax3.set_title("20-Day MA Change Rate")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Change Rate")
    ax3.tick_params(axis='x', labelsize=8)
    ax3.grid(True)
    ax3.legend()
    fig3.autofmt_xdate(rotation=45)
    st.pyplot(fig3)