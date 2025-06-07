import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

def format_volume(volume):
    """將成交量轉為數字格式（整數）"""
    try:
        return int(float(volume))
    except:
        return volume

def format_zscore(z):
    """Z-score 顯示格式，若為數字則四捨五入，否則顯示 NaN"""
    if pd.isna(z):
        return "NaN"
    try:
        return round(z, 2)
    except:
        return "NaN"

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確保 Volume 欄為純數字
    data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 zscore（保留 NaN）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 建立顯示用的 DataFrame（不轉萬單位，保留 NaN）
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = display_data["zscore_volume"].apply(format_zscore)

    # 顯示最近 30 筆資料（保留所有值）
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))