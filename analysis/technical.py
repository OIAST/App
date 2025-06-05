import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol: str, data: pd.DataFrame):
    st.subheader(f"📊 技術面分析 - {symbol}")

    # 🧪 檢查 Volume 欄位
    if "Volume" not in data.columns:
        st.error("❌ 無法進行分析：資料中缺少 Volume 欄位")
        return

    if data["Volume"].dropna().empty:
        st.error("❌ 無法進行分析：Volume 資料為空")
        return

    # ✅ 計算 z-score 成交量異常
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 🔎 檢查欄位是否計算成功
    required_cols = ["volume_ma20", "volume_std20", "zscore_volume"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"❌ 缺少欄位：{missing_cols}")
        return

    data_clean = data.dropna(subset=required_cols + ["Volume"]).copy()
    if data_clean.empty:
        st.warning("⚠️ 無法繪製圖表，z-score 資料不足")
        return

    # 📈 繪製圖表
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean["zscore_volume"],
        mode="lines",
        name="Z-score Volume",
        line=dict(color="blue")
    ))

    fig.add_hline(y=2, line_dash="dash", line_color="red", annotation_text="異常高")
    fig.add_hline(y=-2, line_dash="dash", line_color="green", annotation_text="異常低")

    fig.update_layout(
        title="成交量 Z-score 異常分析",
        xaxis_title="日期",
        yaxis_title="Z-score",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)