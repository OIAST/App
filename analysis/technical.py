import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def run(symbol):
    st.subheader("📊 技術分析圖表")

    try:
        data = yf.download(symbol, period="3mo", interval="1d")
    except Exception as e:
        st.error(f"資料載入錯誤：{e}")
        return

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 找不到成交量資料")
        return

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 確認欄位是否存在
    missing_cols = [col for col in ["volume_ma20", "volume_std20"] if col not in data.columns]
    if missing_cols:
        st.error(f"⚠️ 缺少欄位：{missing_cols}")
        return

    # 檢查是否全為 NaN（例如資料太少）
    if data[["volume_ma20", "volume_std20"]].isna().all().any():
        st.warning("⚠️ 無法計算移動平均，資料可能不足")
        return

    # 清除 NaN 資料
    data = data.dropna(subset=["volume_ma20", "volume_std20"])

    # 計算 z-score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 畫圖
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data["zscore_volume"], name="Z-Score Volume"))
    fig.update_layout(title=f"{symbol} - 成交量 Z-Score", xaxis_title="日期", yaxis_title="Z-Score")
    st.plotly_chart(fig)

    st.dataframe(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(10))