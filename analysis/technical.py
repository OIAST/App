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

    # 抓取近 90 天資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或缺少 Volume 欄位。")
        return

    # 計算 20MA 與 20STD
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 zscore_volume
    data["zscore_volume"] = (
        (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    )

    # ⚠️ 在這裡先建立「乾淨版」資料，只保留 zscore 有值的行
    clean_data = data.dropna(subset=["zscore_volume"]).copy()

    # 顯示用表格格式化
    display_data = clean_data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))