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

    # 抓取資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確保 Volume 存在且為數字
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    data["Volume"] = data["Volume"].apply(safe_float)

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 確認欄位存在
    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"❌ 缺少欄位：{missing_cols}，無法計算 z-score。")
        return

    # 計算 z-score
    valid = data.dropna(subset=required_cols)
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data.loc[valid.index, "zscore_volume"] = zscore

    # 顯示結果（只印出純數字）
    recent_data = data.dropna(subset=["zscore_volume"]).tail(30)
    st.write("🔢 近 30 日成交量分析（純數字）")
    for date, row in recent_data.iterrows():
        st.write(
            f"📅 {date.date()}｜Volume: {int(row['Volume'])}｜MA20: {int(row['volume_ma20'])}｜STD20: {int(row['volume_std20'])}｜Z-Score: {row['zscore_volume']:.2f}"
        )