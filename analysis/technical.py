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

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 檢查欄位是否成功產生後再 dropna
    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    if not all(col in data.columns for col in required_cols):
        st.error("⚠️ 缺少必要欄位，無法計算 zscore。")
        return

    # 將 zscore 計算應用於完整資料行
    temp = data[required_cols].copy()
    temp = temp.dropna()
    data["zscore_volume"] = None  # 預設先填 None
    data.loc[temp.index, "zscore_volume"] = (
        (temp["Volume"] - temp["volume_ma20"]) / temp["volume_std20"]
    )

    # 準備顯示資料
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)

    # 處理 zscore 格式轉換與四捨五入（避免 None 報錯）
    display_data["zscore_volume"] = pd.to_numeric(display_data["zscore_volume"], errors="coerce").round(2)

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))