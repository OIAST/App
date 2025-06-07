import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(volume):
    """將成交量轉換成含萬的格式"""
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

    # 抓取 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20MA 和 20STD
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 直接計算 zscore_volume，NaN 自動處理掉
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示用 DataFrame
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)

    # 確保 zscore 是數字格式再四捨五入
    display_data["zscore_volume"] = pd.to_numeric(display_data["zscore_volume"], errors="coerce").round(2)

    # 顯示
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))