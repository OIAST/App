import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    # 抓資料
    data = yf.download(symbol, period="3mo", interval="1d", auto_adjust=True)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得股價或成交量資料")
        return

    # 計算量的移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 只有在欄位真的存在時才 dropna
    expected_cols = ["volume_ma20", "volume_std20"]
    available_cols = [col for col in expected_cols if col in data.columns]

    if not available_cols:
        st.error("⚠️ 必要欄位不存在，無法計算 z-score")
        return

    data = data.dropna(subset=available_cols)

    # 再保證沒有 NAN 才做計算
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

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