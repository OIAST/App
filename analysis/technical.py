import streamlit as st
import yfinance as yf
import pandas as pd

# Z-score 計算邏輯，避開 NaN 與除以 0 問題
def safe_zscore(row):
    vol = row["Volume"]
    ma = row["volume_ma20"]
    std = row["volume_std20"]
    if pd.isna(vol) or pd.isna(ma) or pd.isna(std) or std == 0:
        return float("nan")
    return (vol - ma) / std

# 主分析函式
def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 顯示原始 Volume 資料型別（用於 debug）
    st.write("📌 Volume 原始資料類型：", str(type(data["Volume"].iloc[-1])))

    # 計算 20 日均量與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 Z-score，避開錯誤
    data["zscore_volume"] = data.apply(safe_zscore, axis=1)

    # 顯示最近 30 筆資料（含 Z-score）
    st.write("📈 成交量統計與 Z-score（近 30 日）")
    display_cols = ["Volume", "volume_ma20", "volume_std20", "zscore_volume"]
    display_data = data[display_cols].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    st.dataframe(display_data.tail(30))

# Streamlit UI
st.title("📈 股票技術面分析工具")
symbol = st.text_input("請輸入股票代碼（如：AAPL、TSLA、2330.TW）：", value="2330.TW")

if symbol:
    run(symbol)