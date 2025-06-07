import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 技術分析選單
    analysis_option = st.selectbox(
        "選擇技術分析類型",
        ["統計量化分析", "A", "B", "C"]
    )
    st.write(f"目前選擇：{analysis_option}")

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
    # 計算標準差變動率
    data["volume_std20_change"] = data["volume_std20"].pct_change()

    # 篩選最近 30 筆資料
    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%y/%m/%d")

    # 股價走勢圖 (Close)
    st.write("📉 股價走勢 (Close)")
    fig_close, ax_close = plt.subplots(figsize=(10, 3))
    ax_close.plot(dates, recent_data["Close"], color="green", label="Close Price")
    ax_close.set_title("Stock Closing Price")
    ax_close.set_xlabel("Date")
    ax_close.set_ylabel("Price")
    ax_close.tick_params(axis='x', labelsize=8)
    ax_close.grid(True)
    ax_close.legend()
    fig_close.autofmt_xdate(rotation=45)
    st.pyplot(fig_close)

    # 成交量與 MA 折線圖
    st.write("📈 Volume & 20-Day MA")
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

if __name__ == "__main__":
    st.title("股票技術分析工具")
    stock_input = st.text_input("輸入股票代碼（例如 AAPL）", value="AAPL")
    if stock_input:
        run(stock_input.upper())