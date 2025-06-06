import yfinance as yf
import streamlit as st
import pandas as pd

def format_volume(v):
    """格式化成交量，超過萬則加上 '萬' 並縮寫"""
    try:
        if pd.isna(v):
            return "N/A"
        elif v >= 1_0000:
            return f"{v/1_0000:.2f}萬"
        else:
            return f"{v:.0f}"
    except:
        return "N/A"

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取1年資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20日均量與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["zscore_volume"] = float("nan")  # 預設為 NaN

    # 安全地計算 z-score 並寫入正確的 index
    valid = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data.loc[zscore.index, "zscore_volume"] = zscore

    # 最後30筆資料拿來顯示
    display_df = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30).copy()
    display_df["Volume"] = display_df["Volume"].apply(format_volume)
    display_df["volume_ma20"] = display_df["volume_ma20"].apply(format_volume)
    display_df["volume_std20"] = display_df["volume_std20"].apply(format_volume)
    display_df["zscore_volume"] = display_df["zscore_volume"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

    st.write("📈 成交量 Z-score（最後30日）：")
    st.dataframe(display_df)