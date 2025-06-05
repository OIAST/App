import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol, data):
    st.subheader(f"📊 技術面分析 - {symbol}")

    # 檢查 Volume 欄位是否存在且有效
    if "Volume" not in data.columns:
        st.error("❌ 此股票資料中缺少 'Volume' 欄位，無法進行技術分析。")
        return

    if data["Volume"].isnull().all():
        st.error("❌ 無法進行分析，Volume 欄位全為空值。")
        return

    # 建立技術指標欄位
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 過濾有效資料
    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    available_cols = [col for col in required_cols if col in data.columns]

    if len(available_cols) < len(required_cols):
        st.warning(f"⚠️ 缺少欄位：{list(set(required_cols) - set(available_cols))}")
        return

    data_clean = data.dropna(subset=required_cols).copy()

    # 計算 z-score volume
    data_clean["zscore_volume"] = (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]

    # 畫出 z-score 成交量圖
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_clean.index, y=data_clean["zscore_volume"],
                             mode="lines", name="Z-score Volume",
                             line=dict(color="royalblue")))
    fig.update_layout(
        title="Z-score Volume 分析",
        xaxis_title="日期",
        yaxis_title="Z-score",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)