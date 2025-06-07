import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(volume):
    try:
        volume = float(volume)
        if volume >= 10_000:
            return f"{volume / 10000:.1f} 萬"
        else:
            return f"{volume:.0f}"
    except:
        return volume

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或缺少 Volume 欄位。")
        return

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 初始化 z-score 欄位
    data["zscore_volume"] = None

    # 計算 z-score
    valid = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    if not valid.empty:
        zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
        data.loc[valid.index, "zscore_volume"] = zscore

    # 建立顯示用的 DataFrame（含轉換格式）
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = display_data["zscore_volume"].astype(float).round(2)

    # 顯示近 30 筆有 Z-score 的資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.dropna(subset=["zscore_volume"]).tail(30))