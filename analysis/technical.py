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

    # 計算移動平均和標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 只選擇那些實際存在的欄位來做 dropna
    requested_cols = ["volume_ma20", "volume_std20"]
    existing_cols = [col for col in requested_cols if col in data.columns]

    if existing_cols:
        data = data.dropna(subset=existing_cols)
        if data.empty:
            st.warning("⚠️ 資料在 dropna 後為空，無法分析")
            return
    else:
        st.error("❌ 無任何有效欄位 volume_ma20 / volume_std20，請檢查資料來源或股票代碼")
        st.write("目前欄位：", data.columns.tolist())
        return

    # 計算 z-score（注意：這裡資料已被 dropna 清理過）
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

    # 顯示 z-score 折線圖
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data.index,
        y=data["zscore_volume"],
        mode="lines",
        name="Z-score Volume"
    ))
    fig2.update_layout(title="成交量 Z-score 指標", xaxis_title="日期", yaxis_title="Z-score")
    st.plotly_chart(fig2, use_container_width=True)