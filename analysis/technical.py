# analysis/technical.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol, data):
    st.subheader("📊 技術面分析")

    # ✅ 安全檢查 Volume 欄位是否存在
    if "Volume" not in data.columns:
        st.error("⚠️ 無法取得 Volume 欄位，資料遺失。")
        st.dataframe(data.head())
        return

    if data["Volume"].isnull().all():
        st.error("⚠️ Volume 欄位全為空值，無法分析。")
        st.dataframe(data.head())
        return

    # ✅ 計算成交量移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    missing_cols = [col for col in required_cols if col not in data.columns]

    if missing_cols:
        st.error(f"⚠️ 欄位遺失：{missing_cols}")
        st.dataframe(data.head())
        return

    # ✅ 清除缺失值行
    data_clean = data.dropna(subset=required_cols).copy()

    if data_clean.empty:
        st.error("⚠️ 無足夠資料計算技術指標")
        st.dataframe(data.tail())
        return

    # ✅ 計算 Z-score 成交量
    data_clean["zscore_volume"] = (
        (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]
    )

    # ✅ 成交量折線圖
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean["Volume"],
        mode="lines",
        name="Volume"
    ))
    fig_volume.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean["volume_ma20"],
        mode="lines",
        name="MA20"
    ))
    fig_volume.update_layout(title="每日成交量與 20 日均量", xaxis_title="日期", yaxis_title="成交量")
    st.plotly_chart(fig_volume, use_container_width=True)

    # ✅ Z-score 圖
    fig_zscore = go.Figure()
    fig_zscore.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean["zscore_volume"],
        mode="lines",
        name="Z-score Volume"
    ))
    fig_zscore.update_layout(title="Z-score 成交量", xaxis_title="日期", yaxis_title="Z-score")
    st.plotly_chart(fig_zscore, use_container_width=True)