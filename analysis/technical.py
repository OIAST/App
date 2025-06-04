import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


def fetch_rsi(symbol: str, period: str = "7d", interval: str = "1h", window: int = 14):
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty:
        return None, None

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return df, rsi


def render_rsi_bar(symbol: str):
    df, rsi = fetch_rsi(symbol)
    if df is None or rsi is None or rsi.empty:
        st.warning("無法取得 RSI 或股價資料")
        return

    current_price = df["Close"].iloc[-1]
    if pd.isna(current_price) or current_price == 0:
        st.warning("無法取得目前股價")
        return

    current_rsi = rsi.iloc[-1]
    if pd.isna(current_rsi):
        st.warning("無法計算 RSI")
        return

    low_rsi = 30
    high_rsi = 70

    # 計算 RSI 30 與 70 對應的價格範圍（以 RSI 線性推估）
    min_rsi = rsi.min()
    max_rsi = rsi.max()

    if min_rsi == max_rsi:
        st.warning("RSI 資料不足以推估價格區間")
        return

    min_price = df["Close"].min()
    max_price = df["Close"].max()

    low_rsi_price = min_price + (low_rsi - min_rsi) / (max_rsi - min_rsi) * (max_price - min_price)
    high_rsi_price = min_price + (high_rsi - min_rsi) / (max_rsi - min_rsi) * (max_price - min_price)

    # 畫出 RSI 價格位置 bar 條
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=current_price,
        delta={'reference': low_rsi_price, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [low_rsi_price, high_rsi_price]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [low_rsi_price, current_price], 'color': "lightblue"},
                {'range': [current_price, high_rsi_price], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': current_price
            }
        },
        title={'text': f"{symbol} RSI 價格區間"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=30, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)


def run(symbol: str):
    st.subheader("📉 技術面分析：RSI")
    render_rsi_bar(symbol)