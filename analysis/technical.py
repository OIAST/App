import streamlit as st
import yfinance as yf
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取 90 天資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確保 Volume 為整數
    data["Volume"] = data["Volume"].fillna(0).astype(int)

    # 計算 20MA 與 20STD 並轉為整數
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean().fillna(0).astype(int)
    data["volume_std20"] = data["Volume"].rolling(window=20).std().fillna(0).astype(int)

    # 計算 Z-score（避免除以 0）
    data["zscore_volume"] = 0
    mask = data["volume_std20"] != 0
    data.loc[mask, "zscore_volume"] = (
        (data.loc[mask, "Volume"] - data.loc[mask, "volume_ma20"]) // data.loc[mask, "volume_std20"]
    )

    # 顯示最近 30 筆
    st.write("📈 近 30 日成交量 Z-score（以整數表示）")
    display_cols = ["Volume", "volume_ma20", "volume_std20", "zscore_volume"]
    st.dataframe(data[display_cols].tail(30))

# Streamlit 頁面
st.title("📈 技術面分析（整數簡化版）")
symbol = st.text_input("輸入股票代碼（例如：2330.TW、AAPL）：", value="2330.TW")

if symbol:
    run(symbol)