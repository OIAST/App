import yfinance as yf
import streamlit as st
import plotly.graph_objs as go

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓六個月日線資料
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得有效資料或資料中缺少 Volume 欄位。")
        return

    # 計算 MA20 與 Std20，並避免 NaN 的資料被立即使用
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 安全方式：建立新欄位前先過濾出合法資料
    mask = data["volume_std20"].notna()
    data.loc[mask, "zscore_volume"] = (data.loc[mask, "Volume"] - data.loc[mask, "volume_ma20"]) / data.loc[mask, "volume_std20"]

    # 如果還是找不到 zscore_volume，錯誤提醒
    if "zscore_volume" not in data.columns:
        st.error("⚠️ 無法正確計算 z-score，可能因為資料不足。")
        return

    # Plotly 繪圖
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

    # 顯示最後 30 筆資料
    st.dataframe(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30))