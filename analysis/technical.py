import yfinance as yf
import streamlit as st
import pandas as pd

def safe_float(x):
    try:
        return float(x)
    except:
        return None

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    data["Volume"] = data["Volume"].apply(safe_float)

    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    valid = data.dropna(subset=["Volume", "volume_ma20", "volume_std20"])
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data.loc[valid.index, "zscore_volume"] = zscore

    # 確認欄位名存在
    required_cols = ["volume_ma20", "volume_std20", "zscore_volume"]
    for col in required_cols:
        if col not in data.columns:
            st.error(f"⚠️ 欄位 {col} 不存在，請檢查資料。")
            return

    recent_data = data.dropna(subset=required_cols).tail(30)

    st.write("🔢 近 30 日成交量分析（純數字呈現）")
    for date, row in recent_data.iterrows():
        st.write(f"📅 {date.date()}｜Volume: {int(row['Volume'])}｜MA20: {int(row['volume_ma20'])}｜STD20: {int(row['volume_std20'])}｜Z-Score: {row['zscore_volume']:.2f}")