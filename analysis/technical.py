import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def render_rsi_bar(symbol: str):
    df = yf.download(symbol, period="6mo", interval="1d")
    if df.empty:
        st.error("無法取得股價資料")
        return

    df["RSI"] = calculate_rsi(df)
    df.dropna(inplace=True)

    current_price = df["Close"].iloc[-1].item()  # 轉成 float 避免 ValueError
    current_rsi = df["RSI"].iloc[-1]

    low_rsi = 30
    high_rsi = 70

    # 推估 RSI 30 與 70 所對應的價格（假設價格與 RSI 線性相關）
    rsi_range = df["RSI"].max() - df["RSI"].min()
    price_range = df["Close"].max() - df["Close"].min()

    try:
        slope = price_range / rsi_range if rsi_range != 0 else 1
        low_rsi_price = df["Close"].min() + (30 - df["RSI"].min()) * slope
        high_rsi_price = df["Close"].min() + (70 - df["RSI"].min()) * slope
    except:
        low_rsi_price, high_rsi_price = current_price * 0.9, current_price * 1.1

    low_rsi_price = round(low_rsi_price, 2)
    high_rsi_price = round(high_rsi_price, 2)

    fig = go.Figure()

    # RSI 區間條 (30~70)
    fig.add_trace(go.Bar(
        x=["RSI"],
        y=[high_rsi_price - low_rsi_price],
        base=[low_rsi_price],
        orientation='v',
        name='RSI 區間',
        marker=dict(color='lightgray'),
        hovertext=[f"RSI 30 價格: {low_rsi_price}<br>RSI 70 價格: {high_rsi_price}"],
        hoverinfo='text'
    ))

    # 現價標示
    fig.add_trace(go.Scatter(
        x=["RSI"],
        y=[current_price],
        mode="markers+text",
        name="現價",
        text=[f"現價 {current_price:.2f}"],
        textposition="top center",
        marker=dict(color="red", size=12)
    ))

    fig.update_layout(
        title=f"{symbol} RSI 現價位置",
        height=400,
        yaxis_title="價格區間",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def run(symbol: str):
    st.subheader("📊 技術面指標分析")
    render_rsi_bar(symbol)