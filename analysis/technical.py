import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def run(symbol):
    st.subheader(f"📊 技術面分析（成交量）：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 計算 20 日移動平均與標準差
    data["Volume"] = data["Volume"].fillna(0).astype(int)
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 顯示原始數據表格（近 30 筆）
    display_data = data[["Volume", "volume_ma20", "volume_std20"]].copy()
    st.write("📋 成交量統計數據（近 30 日）")
    st.dataframe(display_data.tail(30))

    # 畫靜態折線圖
    st.write("📈 成交量折線圖（含 20 日均量與標準差）")
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(data.index, data["Volume"], label="Volume", color="skyblue")
    ax.plot(data.index, data["volume_ma20"], label="20日均量", color="orange")
    ax.plot(data.index, data["volume_std20"], label="20日標準差", color="green", linestyle="--")

    ax.set_title("成交量分析圖")
    ax.set_xlabel("日期")
    ax.set_ylabel("成交量")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)