import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(volume):
    """將成交量數字轉為含萬單位（例：12.3 萬）"""
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

    # 抓取近 1 年日線資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 z-score：僅套用在三個欄位都非 NaN 的 row
    valid_rows = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    zscore = (valid_rows["Volume"] - valid_rows["volume_ma20"]) / valid_rows["volume_std20"]
    data.loc[valid_rows.index, "zscore_volume"] = zscore

    # 準備顯示表格：這裡才格式化數值
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()

    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30), use_container_width=True)