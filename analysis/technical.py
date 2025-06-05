import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    # 取得資料
    data = yf.download(symbol, period="3mo", interval="1d", auto_adjust=True)
    
    if data.empty or "Volume" not in data.columns:
        st.warning("無法取得股價資料")
        return

    # 計算 20 日均量與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 避免 NaN 錯誤：先篩選出可用欄位
    data = data.copy()
    data = data[data["volume_ma20"].notna() & data["volume_std20"].notna()]

    # 計算 z-score volume（異常量能指標）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    if data.empty:
        st.warning("計算 z-score volume 失敗，請確認股票代碼或資料期間。")
        return

    # 繪製圖表
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data["zscore_volume"], name="Z-score Volume", marker_color="orange"))
    fig.update_layout(title=f"{symbol} - 異常量能 z-score",
                      xaxis_title="日期", yaxis_title="z-score",
                      height=400)
    st.plotly_chart(fig, use_container_width=True)