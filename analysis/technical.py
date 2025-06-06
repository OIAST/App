import yfinance as yf
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取6個月日線資料
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或資料中缺少 Volume 欄位。")
        return

    # ✅ 先建立 MA 與 STD 欄位
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # ✅ 確保欄位存在後再 dropna
    if "volume_ma20" not in data.columns or "volume_std20" not in data.columns:
        st.error("⚠️ 計算 MA 與 STD 時出現問題。")
        return

    # ✅ 這時欄位已經存在，可以 dropna
    data_filtered = data.dropna(subset=["volume_ma20", "volume_std20"]).copy()
    data_filtered["zscore_volume"] = (
        (data_filtered["Volume"] - data_filtered["volume_ma20"]) / data_filtered["volume_std20"]
    )

    # ✅ 繪圖
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data_filtered.index,
        y=data_filtered["Volume"],
        name="Volume",
        marker_color="rgba(158,202,225,0.6)",
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=data_filtered.index,
        y=data_filtered["volume_ma20"],
        name="MA20",
        line=dict(color="blue"),
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=data_filtered.index,
        y=data_filtered["zscore_volume"],
        name="Z-Score",
        line=dict(color="red", dash="dot"),
        yaxis="y2"
    ))

    fig.update_layout(
        title=f"{symbol} Volume 與 Z-Score",
        xaxis_title="日期",
        yaxis=dict(title="Volume", side="left", showgrid=False),
        yaxis2=dict(title="Z-Score", overlaying="y", side="right", showgrid=False),
        legend=dict(x=0, y=1.1, orientation="h"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data_filtered[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30))