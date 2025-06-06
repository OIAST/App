# technical.py
import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objs as go

def run(symbol):
    st.subheader("📊 技術面分析")

    # 抓資料
    try:
        data = yf.download(symbol, period="3mo", interval="1d")
    except Exception as e:
        st.error(f"❌ 無法下載資料：{e}")
        return

    # 檢查資料與 Volume 欄位是否存在
    if data.empty:
        st.warning("⚠️ 資料為空，請確認股票代碼是否正確")
        return
    if "Volume" not in data.columns:
        st.warning("⚠️ 資料中沒有 Volume 欄位")
        return
    if data["Volume"].isnull().all():
        st.warning("⚠️ Volume 資料全為空值")
        return

    # 計算移動平均與 Z-score
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 檢查欄位是否有 NaN，避免報錯
    if data[["volume_ma20", "volume_std20"]].isnull().all().any():
        st.warning("⚠️ 無法計算 Z-score，移動平均或標準差為空")
        return

    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 畫圖
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data["Volume"], mode='lines', name='Volume'))
    fig.add_trace(go.Scatter(x=data.index, y=data["volume_ma20"], mode='lines', name='MA20'))
    fig.add_trace(go.Scatter(x=data.index, y=data["zscore_volume"], mode='lines', name='Z-Score'))

    fig.update_layout(title=f"{symbol} 成交量技術指標",
                      xaxis_title="日期", yaxis_title="數值")

    st.plotly_chart(fig, use_container_width=True)