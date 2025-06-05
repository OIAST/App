import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

def run(symbol: str):
    st.subheader(f"📈 技術面分析 - {symbol}")

    data = yf.download(symbol, interval="1d", period="6mo")

    if data.empty:
        st.error("❌ 無法取得資料，請確認股票代碼")
        return

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 檢查要使用的欄位是否存在於 DataFrame
    subset_cols = ["volume_ma20", "volume_std20"]
    missing_cols = [col for col in subset_cols if col not in data.columns]

    if missing_cols:
        st.error(f"❌ 缺少欄位：{missing_cols}，無法繼續計算")
        st.write("現有欄位：", data.columns.tolist())
        return

    try:
        data = data.dropna(subset=subset_cols).copy()
    except KeyError as e:
        st.error(f"⚠️ dropna 時欄位錯誤：{e}")
        return

    if data.empty:
        st.warning("⚠️ 資料在 dropna 後為空，請更換股票代碼或時間區間")
        return

    # 計算 z-score volume
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 畫 K 線圖
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="K 線"
        )
    ])
    fig.update_layout(title=f"{symbol} K 線圖", xaxis_title="日期", yaxis_title="價格")
    st.plotly_chart(fig, use_container_width=True)

    # 畫 Z-score 成交量
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data.index,
        y=data["zscore_volume"],
        mode="lines",
        name="Z-score Volume"
    ))
    fig2.update_layout(title="成交量 Z-score", xaxis_title="日期", yaxis_title="Z-score")
    st.plotly_chart(fig2, use_container_width=True)