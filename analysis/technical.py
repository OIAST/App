import yfinance as yf
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 直接從 yfinance 抓一次完整資料即可，這會由主程式統一提供
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或資料中缺少 Volume 欄位。")
        return

    # 這裡不用檢查 NaN，直接信任 data 完整性，從已有欄位處理
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 如果真的有極端狀況欄位不存在，這裡才提醒
    required_cols = ["Volume", "volume_ma20", "volume_std20", "zscore_volume"]
    for col in required_cols:
        if col not in data.columns:
            st.error(f"⚠️ 缺少欄位：{col}，請確認資料是否完整。")
            return

    # 繪圖
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data.index,
        y=data["Volume"],
        name="Volume",
        marker_color="rgba(158,202,225,0.6)",
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["volume_ma20"],
        name="MA20",
        line=dict(color="blue"),
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["zscore_volume"],
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
    st.dataframe(data[required_cols].tail(30))