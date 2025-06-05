# technical.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol, data: pd.DataFrame):
    st.subheader("📊 技術面分析 - Volume Z-score")

    if "Volume" not in data.columns:
        st.warning("⚠️ 請提供包含 Volume 欄位的 DataFrame")
        return

    # ✅ 先計算這些欄位
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # ✅ 再做 dropna，避免欄位不存在時報錯
    try:
        data_clean = data.dropna(subset=["volume_ma20", "volume_std20", "Volume"]).copy()
    except KeyError as e:
        st.warning(f"⚠️ 欄位遺失：{e}")
        return

    if data_clean.empty:
        st.warning("⚠️ 無足夠資料進行技術分析")
        return

    # ✅ 計算 Z-score
    data_clean["zscore_volume"] = (
        (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]
    )

    # ✅ 畫圖
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_clean.index, y=data_clean["zscore_volume"], mode='lines', name='Volume Z-score'))
    fig.update_layout(title=f"{symbol} Volume Z-score（20日）", xaxis_title="Date", yaxis_title="Z-score")
    st.plotly_chart(fig, use_container_width=True)