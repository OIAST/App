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

    # 確保 Volume 為數值格式
    data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 Z-score
    valid = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data.loc[valid.index, "zscore_volume"] = zscore

    # 建立顯示用的 DataFrame（不轉換萬單位）
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))