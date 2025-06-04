import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


def render_rsi_bar(symbol: str):
    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty:
        st.warning("找不到股票資料")
        return

    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    data["RSI"] = rsi
    current_price = data["Close"].iloc[-1]

    try:
        low_rsi_price = float(data[data["RSI"] <= 30]["Close"].median())
    except:
        low_rsi_price = current_price * 0.9

    try:
        high_rsi_price = float(data[data["RSI"] >= 70]["Close"].median())
    except:
        high_rsi_price = current_price * 1.1

    # 修正 NaN 情況
    if pd.isna(low_rsi_price) or low_rsi_price == 0:
        low_rsi_price = round(current_price * 0.9, 2)
    if pd.isna(high_rsi_price) or high_rsi_price == 0:
        high_rsi_price = round(current_price * 1.1, 2)

    # 建立 RSI 區間 bar
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["RSI區間"],
        y=[high_rsi_price - low_rsi_price],
        base=low_rsi_price,
        marker=dict(color="#d0d0d0"),
        name="30~70 價格區間",
        hoverinfo="none",
    ))

    # 現價線
    fig.add_trace(go.Scatter(
        x=["RSI區間"],
        y=[current_price],
        mode="markers+text",
        marker=dict(color="red", size=14),
        text=[f"現價 {current_price:.2f}"],
        textposition="top center",
        name="現價",
    ))

    fig.update_layout(
        height=250,
        title="RSI 價格區間（30~70）",
        yaxis_title="股價",
        xaxis_showticklabels=False,
        bargap=0.5,
        margin=dict(t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)


def run(symbol: str):
    st.subheader("技術面分析 - RSI 價格區間")
    render_rsi_bar(symbol)