import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

def run(symbol: str):
    st.subheader("📊 技術面分析：成交量異常（Z-score）")

    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
    except Exception as e:
        st.error(f"❌ 資料讀取錯誤：{e}")
        return

    if data.empty or "Volume" not in data.columns:
        st.warning("⚠️ 資料無效或缺少成交量")
        return

    # 1. 計算 MA 與 STD，保證欄位存在
    data["volume_ma20"] = data["Volume"].rolling(window=20, min_periods=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20, min_periods=20).std()

    # 2. 濾除無效資料
    data = data.dropna().copy()
    data = data[data["volume_std20"] != 0]

    # 3. 計算 Z-score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 4. 取最近 60 日畫圖
    recent_data = data.tail(60)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=recent_data.index,
        y=recent_data["zscore_volume"],
        name="Volume Z-score",
        marker_color=np.where(recent_data["zscore_volume"] > 2, 'red', 'blue')
    ))
    fig.update_layout(
        title=f"{symbol} 成交量 Z-score",
        xaxis_title="日期",
        yaxis_title="Z-score",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # 顯示異常日
    abnormal = recent_data[recent_data["zscore_volume"] > 2]
    if not abnormal.empty:
        st.markdown("### 🚨 異常交易日")
        st.dataframe(abnormal[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].round(2))
    else:
        st.info("近期無異常交易量")