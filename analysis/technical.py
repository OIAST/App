import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol, data):
    st.subheader("📊 技術面分析")

    if "Volume" not in data.columns or data["Volume"].isnull().all():
        st.error("⚠️ 無法取得 Volume 資料，請確認該股票是否有交易量資料")
        st.dataframe(data.tail())  # 顯示資料協助除錯
        return

    # 計算技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"❌ 錯誤：缺少欄位 {missing}")
        return

    data_clean = data.dropna(subset=required_cols).copy()
    if data_clean.empty:
        st.warning("⚠️ 經過清理後沒有足夠資料")
        return

    data_clean["zscore_volume"] = (
        (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]
    )

    # 畫圖：成交量與 Z-score
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_clean.index, y=data_clean["zscore_volume"],
                             mode="lines", name="Z-Score Volume"))
    fig.add_trace(go.Scatter(x=data_clean.index, y=data_clean["Volume"],
                             mode="lines", name="Volume", yaxis="y2"))

    fig.update_layout(
        title=f"{symbol} - 成交量與 Z-score",
        xaxis_title="日期",
        yaxis=dict(title="Z-score"),
        yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
        legend=dict(x=0, y=1),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)