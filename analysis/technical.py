import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取一年日線資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    # 檢查資料是否正確取得
    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確認 Volume 欄位是否存在
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20 日平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 顯示近 90 日資料
    st.write("📋 計算結果（近90日）")
    st.dataframe(data[["Volume", "volume_ma20", "volume_std20"]].tail(90))