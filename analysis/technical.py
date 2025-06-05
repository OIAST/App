import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    # 下載股價資料
    data = yf.download(symbol, period="3mo", interval="1d", auto_adjust=True)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得股價或成交量資料")
        return

    # 僅保留需要欄位，轉換為 Series
    volume = data["Volume"].astype(float)

    # 計算 rolling 統計值
    volume_ma20 = volume.rolling(window=20).mean()
    volume_std20 = volume.rolling(window=20).std()

    # 組回 dataframe
    data = data.copy()
    data["volume_ma20"] = volume_ma20
    data["volume_std20"] = volume_std20

    # 濾掉無效值
    data = data.dropna(subset=["volume_ma20", "volume_std20"])

    # 再次保證型別正確
    v = data["Volume"].astype(float)
    ma = data["volume_ma20"].astype(float)
    std = data["volume_std20"].astype(float)

    # z-score 計算
    data["zscore_volume"] = (v - ma) / std

    # 畫圖
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data.index,
        y=data["zscore_volume"],
        name="Z-score Volume",
        marker_color="indianred"
    ))
    fig.update_layout(
        title=f"{symbol} - 異常成交量 z-score",
        xaxis_title="日期",
        yaxis_title="Z-score",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)