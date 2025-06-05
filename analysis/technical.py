import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    # 下載資料
    data = yf.download(symbol, period="3mo", interval="1d", auto_adjust=True)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得股價或成交量資料")
        return

    # 計算 20 日均值與標準差（避免 NaN）
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 確保無 NaN 才能進行 z-score 計算
    mask = data["volume_ma20"].notna() & data["volume_std20"].notna()
    data = data.loc[mask].copy()

    if data.empty:
        st.warning("⚠️ 資料不足，無法計算 z-score")
        return

    # 計算 z-score 成交量
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 繪圖
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data["zscore_volume"], name="Z-score Volume", marker_color="indianred"))
    fig.update_layout(
        title=f"{symbol} - 異常量能 Z-score",
        xaxis_title="日期",
        yaxis_title="Z-score",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)