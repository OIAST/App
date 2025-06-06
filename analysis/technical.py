import yfinance as yf
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取6個月日線資料
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    # 資料檢查
    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或資料中缺少 Volume 欄位。")
        return

    # 計算技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 清理 NaN
    data.dropna(subset=["volume_ma20", "volume_std20", "zscore_volume"], inplace=True)

    # 繪圖：Volume + MA
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

    # 設定雙 Y 軸
    fig.update_layout(
        title=f"{symbol} Volume 與 Z-Score",
        xaxis_title="日期",
        yaxis=dict(
            title="Volume",
            side="left",
            showgrid=False
        ),
        yaxis2=dict(
            title="Z-Score",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(x=0, y=1.1, orientation="h"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # 顯示資料表供比對
    st.dataframe(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30))