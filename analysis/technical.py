# technical.py

import yfinance as yf
import streamlit as st

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取完整日線資料（interval="1d"，不限制期間）
    data = yf.download(symbol, interval="1d", progress=False)

    # 檢查資料是否正確取得
    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確認 Volume 欄位是否存在且有數值
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return


    # 顯示前幾筆資料供確認
    st.write("✅ 資料成功載入，前幾筆如下：")
    st.dataframe(data.head())