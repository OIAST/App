# technical.py
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

def run(symbol):
    st.subheader("📊 技術面分析 - 成交量異常偵測")

    # 抓取資料
    data = yf.download(symbol, period="3mo", interval="1d", progress=False)

    # 檢查資料是否為空
    if data.empty:
        st.error("❌ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 檢查是否包含 Volume 欄位
    if "Volume" not in data.columns or data["Volume"].dropna().empty:
        st.warning("⚠️ 該股票無法取得成交量資料，可能是冷門股票或代碼錯誤。")
        st.write("📋 實際欄位如下：", data.columns.tolist())
        return

    # 計算移動平均與標準差
    try:
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()
    except Exception as e:
        st.warning("⚠️ 無法計算移動平均，欄位遺失")
        st.exception(e)
        return

    # 清除 NaN 資料
    data = data.dropna(subset=["volume_ma20", "volume_std20"]).copy()
    if data.empty:
        st.warning("⚠️ 有效資料不足（需 20 筆以上有成交量的資料），請改查其他股票。")
        return

    # 計算 Z-Score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示最新資料
    st.dataframe(data[["Close", "Volume", "volume_ma20", "zscore_volume"]].tail(10))

    # 畫圖
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["zscore_volume"],
                             mode='lines+markers', name="Z-Score Volume"))
    fig.add_trace(go.Scatter(x=data.index, y=[2]*len(data),
                             mode='lines', name="+2 σ", line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=[-2]*len(data),
                             mode='lines', name="-2 σ", line=dict(dash='dash', color='blue')))
    fig.update_layout(title=f"{symbol} 成交量異常 Z-Score", height=400)
    st.plotly_chart(fig, use_container_width=True)