import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或缺少 Volume 欄位。")
        return

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 印出 Volume、MA20、STD20 的部分資料與型別
    st.write("📋 檢查數據格式（Volume / MA / STD）前 5 筆：")
    st.write(data[["Volume", "volume_ma20", "volume_std20"]].head())
    st.code(str(data[["Volume", "volume_ma20", "volume_std20"]].dtypes), language="python")

    # 計算 z-score（條件：三欄都不為 NaN）
    condition = (
        data["Volume"].notnull() &
        data["volume_ma20"].notnull() &
        data["volume_std20"].notnull()
    )
    data["zscore_volume"] = np.where(
        condition,
        ((data["Volume"] - data["volume_ma20"]) / data["volume_std20"]).round(2),
        np.nan
    )

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30)
    st.dataframe(display_data)