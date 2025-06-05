import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def fetch_rsi(symbol: str, period: int = 14):
    data = yf.download(symbol, period="3mo", interval="1d")
    delta = data["Adj Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return data["Adj Close"], rsi

def price_from_rsi(adj_close, rsi_series, target_rsi):
    valid = (~rsi_series.isna()) & (~adj_close.isna())
    if not valid.any():
        return None
    rsi_filtered = rsi_series[valid]
    price_filtered = adj_close[valid]
    closest_idx = (rsi_filtered - target_rsi).abs().idxmin()
    return price_filtered.loc[closest_idx]

def render_rsi_bar(symbol: str):
    adj_close, rsi = fetch_rsi(symbol)
    current_price = adj_close.iloc[-1]

    low_rsi_price = price_from_rsi(adj_close, rsi, 30)
    high_rsi_price = price_from_rsi(adj_close, rsi, 70)

    if pd.isna(current_price) or current_price == 0:
        st.warning("❌ 無法取得目前股價。")
        return

    if pd.isna(low_rsi_price) or pd.isna(high_rsi_price):
        st.warning("❌ 無法估算 RSI 價格區間。")
        return

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=["RSI 價格區間"],
        x=[high_rsi_price - low_rsi_price],
        base=low_rsi_price,
        orientation='h',
        marker=dict(color='lightgray'),
        hoverinfo='x',
        name='RSI 區間'
    ))

    fig.add_trace(go.Scatter(
        y=["RSI 價格區間"],
        x=[current_price],
        mode="markers+text",
        marker=dict(color="red", size=14),
        text=[f"現價 {current_price:.2f}"],
        textposition="top right",
        name="現價"
    ))

    fig.update_layout(
        title="RSI 價格位置條",
        height=180,
        margin=dict(l=20, r=20, t=30, b=10),
        xaxis=dict(title="價格"),
        yaxis=dict(showticklabels=False),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def run(symbol: str):
    st.subheader("技術指標快速概覽")
    render_rsi_bar(symbol)