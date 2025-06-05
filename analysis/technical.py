# technical.py
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    st.subheader("📈 技術指標：量價異常檢測")

    # 下載歷史資料
    data = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if data.empty:
        st.error("❌ 無法取得資料，請確認股票代碼正確。")
        return

    # 計算 20 日移動平均與標準差（成交量）
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 移除無法計算的列（前 20 日）
    if not {"volume_ma20", "volume_std20"}.issubset(data.columns):
        st.warning("⚠️ 無法計算移動平均，欄位遺失")
        return

    data = data.dropna(subset=["volume_ma20", "volume_std20"]).copy()

    # 計算 z-score（成交量異常）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示資料表
    st.dataframe(data[["Close", "Volume", "volume_ma20", "zscore_volume"]].tail(10))

    # 畫圖：z-score
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data["zscore_volume"],
        mode='lines+markers',
        name="Z-Score Volume"
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=[2]*len(data),
        mode='lines', name="+2 標準差", line=dict(dash='dash', color='red')
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=[-2]*len(data),
        mode='lines', name="-2 標準差", line=dict(dash='dash', color='blue')
    ))

    fig.update_layout(title=f"{symbol} 成交量異常 Z-Score", height=400)
    st.plotly_chart(fig, use_container_width=True)