import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(volume):
    """將成交量轉換為含萬單位格式（例：12.3 萬）"""
    try:
        volume = float(volume)
        if volume >= 10000:
            return f"{volume / 10000:.1f} 萬"
        else:
            return f"{volume:.0f}"
    except:
        return volume

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 下載資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 MA 與 STD
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # dropna 後計算 zscore_volume
    valid = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data["zscore_volume"] = pd.NA  # 先建立欄位
    data.loc[valid.index, "zscore_volume"] = zscore

    # 顯示用 DataFrame，不修改原始 data（避免文字污染數值）
    display_data = data.copy()
    display_data["Volume"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    # 顯示近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30), use_container_width=True)