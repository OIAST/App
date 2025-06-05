# technical.py

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

def run(symbol: str):
    st.subheader("📊 技術面分析：成交量異常（Z-score）")
    
    # 下載資料
    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
    except Exception as e:
        st.error(f"資料抓取錯誤：{e}")
        return
    
    if data.empty or "Volume" not in data.columns:
        st.warning("⚠️ 無法取得有效資料")
        return

    # 計算成交量 Z-score
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 確保欄位存在才進一步計算
    if "volume_ma20" not in data.columns or "volume_std20" not in data.columns:
        st.warning("⚠️ 無法建立 Z-score 所需欄位")
        return

    # 防止除以 0
    data["volume_std20"].replace(0, np.nan, inplace=True)

    # 計算異常 Z-score（成交量）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data.dropna(subset=["zscore_volume"], inplace=True)

    # 顯示最近一段時間
    recent_data = data.tail(60)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=recent_data.index,
        y=recent_data["zscore_volume"],
        name="Volume Z-score",
        marker_color=np.where(recent_data["zscore_volume"] > 2, 'red', 'blue')
    ))

    fig.update_layout(
        title=f"{symbol} 近期成交量異常（Z-score）",
        xaxis_title="日期",
        yaxis_title="Z-score",
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 顯示異常交易日
    abnormal_days = recent_data[recent_data["zscore_volume"] > 2]
    if not abnormal_days.empty:
        st.markdown("### 🚨 異常交易日（Z-score > 2）")
        st.dataframe(abnormal_days[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].round(2))
    else:
        st.info("近期無明顯異常交易量。")