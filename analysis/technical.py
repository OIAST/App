import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 強制轉為 int 後再計算 MA、STD
    data["Volume"] = data["Volume"].fillna(0).astype(int)
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean().astype(int)
    data["volume_std20"] = data["Volume"].rolling(window=20).std().astype(int)

    # 計算 Z-score（無條件計算，不做例外處理）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示格式與數據內容（for debug）
    st.write("🔍 資料型別")
    st.write("Volume dtype:", data["Volume"].dtype)
    st.write("volume_ma20 dtype:", data["volume_ma20"].dtype)
    st.write("volume_std20 dtype:", data["volume_std20"].dtype)
    st.write("zscore_volume dtype:", data["zscore_volume"].dtype)

    st.write("📌 資料值（最後 5 筆）")
    st.write("Volume:", data["Volume"].tail())
    st.write("volume_ma20:", data["volume_ma20"].tail())
    st.write("volume_std20:", data["volume_std20"].tail())
    st.write("zscore_volume:", data["zscore_volume"].tail())

    # 顯示表格
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))