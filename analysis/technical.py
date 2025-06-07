import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

def format_volume(value):
    """將成交量轉換為整數字串，若無效則回傳 NaN 字串"""
    try:
        return int(float(value))
    except:
        return "NaN"

def force_numeric(value):
    """強制轉換為 float，如果錯誤就回傳 np.nan"""
    try:
        return float(value)
    except:
        return np.nan

def calculate_zscore(v, ma, std):
    """若任一為 NaN 或 std 為 0，則回傳 NaN；否則計算 Z-score"""
    if pd.isna(v) or pd.isna(ma) or pd.isna(std) or std == 0:
        return "NaN"
    return round((v - ma) / std, 2)

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 缺少 Volume 資料")
        return

    # 強制轉為數字格式（不使用 pd.to_numeric）
    data["Volume"] = data["Volume"].apply(force_numeric)

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 z-score
    data["zscore_volume"] = data.apply(
        lambda row: calculate_zscore(row["Volume"], row["volume_ma20"], row["volume_std20"]),
        axis=1
    )

    # 建立顯示表格
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)

    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))