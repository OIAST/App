import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def render_rsi_bar(symbol: str):
    data = yf.download(symbol, period="3mo", interval="1d")
    data["RSI"] = compute_rsi(data["Close"], 14)

    current_price = data["Close"].iloc[-1]
    latest_rsi = data["RSI"].iloc[-1]

    low_rsi_price = data[data["RSI"] <= 30]["Close"].median()
    high_rsi_price = data[data["RSI"] >= 70]["Close"].median()

    # 補救：如果極端 RSI 價格缺失，給預設值
    if pd.isna(low_rsi_price):
        low_rsi_price = round(current_price * 0.9, 2)
    if pd.isna(high_rsi_price):
        high_rsi_price = round(current_price * 1.1, 2)

    # 構建 Bar
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=current_price,
        title={'text': "RSI 位置對應股價"},
        gauge={
            'axis': {'range': [low_rsi_price, high_rsi_price]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [low_rsi_price, high_rsi_price], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': current_price
            }
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ✅ 加上 run(symbol)
def run(symbol: str):
    st.subheader("📊 RSI 價格位置視覺化")
    render_rsi_bar(symbol)