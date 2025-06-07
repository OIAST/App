import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 嘗試直接用最簡單邏輯計算 zscore（Volume 改為 float）
    data["zscore_volume"] = (
        (data["Volume"].astype(float) - data["volume_ma20"]) / data["volume_std20"]
    )

    # 印出每欄位的 dtype 與最後5筆值
    print("Volume dtype:", data["Volume"].dtype)
    print(data["Volume"].tail())

    print("volume_ma20 dtype:", data["volume_ma20"].dtype)
    print(data["volume_ma20"].tail())

    print("volume_std20 dtype:", data["volume_std20"].dtype)
    print(data["volume_std20"].tail())

    print("zscore_volume dtype:", data["zscore_volume"].dtype)
    print(data["zscore_volume"].tail())

    # 顯示表格
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))