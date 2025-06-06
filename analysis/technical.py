import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(v):
    try:
        if v >= 1_0000:
            return f"{v / 1_0000:.2f}萬"
        else:
            return f"{v:,.0f}"
    except:
        return v

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 1. 下載一年資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 2. 計算 20MA 與 20STD
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 3. 計算 Z-score，不使用 dropna
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 4. 顯示最近 30 筆資料
    display_data = data.tail(30).copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)

    st.write("✅ 近 30 日 Volume 資訊：")
    st.dataframe(display_data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]])

    # 5. 畫圖（90 日）
    st.line_chart(data[["zscore_volume"]].tail(90))