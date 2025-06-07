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

    # 解析說明區
    analysis_descriptions = {
        "統計量化分析": "此分析包含成交量、20日均線及其標準差的變動率，幫助判斷成交量波動性及股價走勢。",
        "A": "選項 A 的分析說明，待補充。",
        "B": "選項 B 的分析說明，待補充。",
        "C": "選項 C 的分析說明，待補充。",
    }
    st.markdown(f"**分析說明：** {analysis_descriptions.get(analysis_option, '無說明')}")

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
    # 只顯示月/日格式
    dates = recent_data.index.strftime("%m/%d")

    # 用st.columns並排三張圖表，統一大小和對齊
    col1, col2, col3 = st.columns(3)

    fig_size = (5, 3)

    with col1:
        st.write("📉 股價走勢 (Close)")
        fig_close, ax_close = plt.subplots(figsize=fig_size)
        ax_close.plot(dates, recent_data["Close"], color="green", label="Close Price")
        ax_close.set_title("Stock Closing Price")
        ax_close.set_xlabel("Date")
        ax_close.set_ylabel("Price")
        ax_close.tick_params(axis='x', labelsize=8)
        ax_close.grid(True)
        ax_close.legend()
        fig_close.autofmt_xdate(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_close)

    with col2:
        st.write("📈 成交量 & 20日均線")
        fig_vol, ax_vol = plt.subplots(figsize=fig_size)
        ax_vol.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
        ax_vol.plot(dates, recent_data["volume_ma20"], label="20-Day MA", color="orange")
        ax_vol.set_title("Volume and 20-Day MA")
        ax_vol.set_xlabel("Date")
        ax_vol.set_ylabel("Volume")
        ax_vol.tick_params(axis='x', labelsize=8)
        ax_vol.legend()
        ax_vol.grid(True)
        fig_vol.autofmt_xdate(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_vol)

    with col3:
        st.write("📉 20日標準差變動率")
        fig_std, ax_std = plt.subplots(figsize=fig_size)
        ax_std.plot(dates, recent_data["volume_std20_change"], color="purple", label="STD Change Rate")
        ax_std.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax_std.set_title("20-Day STD Change Rate")
        ax_std.set_xlabel("Date")
        ax_std.set_ylabel("Change Rate")
        ax_std.tick_params(axis='x', labelsize=8)
        ax_std.legend()
        ax_std.grid(True)
        fig_std.autofmt_xdate(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_std)

if __name__ == "__main__":
    st.title("股票技術分析工具")
    stock_input = st.text_input("輸入股票代碼（例如 AAPL）", value="AAPL")
    if stock_input:
        run(stock_input.upper())