import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析（含 Z-score）：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或缺少 Volume 欄位。")
        return

    # ⛳ 將 Volume 轉為 float，避免 int 與 float 衝突
    data["Volume"] = data["Volume"].astype(float)

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 Z-score，確保無法計算時為 NaN
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示最近 30 筆資料
    st.write("📈 成交量統計與 Z-score（近 30 日）")
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30)
    st.dataframe(display_data)

    # 顯示每欄位的資料型別
    st.write("📋 資料欄位型別")
    st.code(str(display_data.dtypes), language="python")

    # 顯示前三筆原始數值
    st.write("🔍 欄位數值預覽")
    st.code("Volume:\n" + str(display_data["Volume"].head(3)) + "\n\n" +
            "volume_ma20:\n" + str(display_data["volume_ma20"].head(3)) + "\n\n" +
            "volume_std20:\n" + str(display_data["volume_std20"].head(3)) + "\n\n" +
            "zscore_volume:\n" + str(display_data["zscore_volume"].head(3)))