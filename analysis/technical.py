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

    # 下載近 90 天的日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 此股票無成交量資料。")
        return

    # 計算 20 日平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 zscore_volume，只對有值的行計算
    valid = data.dropna(subset=["Volume", "volume_ma20", "volume_std20"])
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data.loc[valid.index, "zscore_volume"] = zscore

    # 建立顯示用 DataFrame
    display_data = data.copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = pd.to_numeric(display_data["zscore_volume"], errors="coerce").round(2)

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30))