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

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 z-score（如果無法計算則設為 NaN）
    def compute_zscore(row):
        if pd.notna(row["Volume"]) and pd.notna(row["volume_ma20"]) and pd.notna(row["volume_std20"]) and row["volume_std20"] != 0:
            return (row["Volume"] - row["volume_ma20"]) / row["volume_std20"]
        else:
            return None

    data["zscore_volume"] = data.apply(compute_zscore, axis=1)

    # 建立顯示用表格（不轉換萬單位）
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))