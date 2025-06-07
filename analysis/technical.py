import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或缺少 Volume 欄位。")
        return

    # 計算 20 日成交量移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 直接計算 Z-score，不做條件檢查
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["zscore_volume"] = data["zscore_volume"].round(2)

    # 顯示最近 30 筆資料（不轉換單位）
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30)
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data)