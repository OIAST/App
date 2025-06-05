# technical.py
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def run(symbol: str):
    st.subheader(f"📈 技術面分析 - {symbol}")

    data = yf.download(symbol, interval="1d", period="6mo")
    if data.empty:
        st.error("❌ 無法抓取資料，請確認股票代碼是否正確")
        return

    # 計算移動平均和 z-score（含防錯）
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 檢查欄位是否存在再進行 dropna
    subset_cols = [col for col in ["volume_ma20", "volume_std20"] if col in data.columns]
    if subset_cols:
        data = data.dropna(subset=subset_cols)
        if data.empty:
            st.warning("⚠️ 資料全被 drop 掉，無法繼續分析")
            return
    else:
        st.warning("⚠️ volume_ma20 / volume_std20 欄位不存在，無法進行分析")
        st.write("目前欄位：", data.columns.tolist())
        return

    # 安全計算 z-score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示 K 線圖
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="K線"
        )
    ])
    fig.update_layout(title=f"{symbol} K 線圖", xaxis_title="日期", yaxis_title="價格")
    st.plotly_chart(fig, use_container_width=True)

    # 顯示 z-score Volume 折線圖
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data.index,
        y=data["zscore_volume"],
        mode="lines",
        name="Z-score Volume"
    ))
    fig2.update_layout(title="成交量 Z-score 指標", xaxis_title="日期", yaxis_title="Z-score")
    st.plotly_chart(fig2, use_container_width=True)