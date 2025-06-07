import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 計算 20 日移動平均與標準差，並強制轉成 int
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean().fillna(0).astype(int)
    data["volume_std20"] = data["Volume"].rolling(window=20).std().fillna(0).astype(int)
    data["Volume"] = data["Volume"].fillna(0).astype(int)

    # 計算 Z-score（若 std 為 0，則結果設為 NaN）
    data["zscore_volume"] = np.where(
        data["volume_std20"] != 0,
        (data["Volume"] - data["volume_ma20"]) / data["volume_std20"],
        np.nan
    )

    # 顯示格式與數據內容
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