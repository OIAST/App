import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def fetch_rsi(symbol: str, period: int = 14):
    data = yf.download(symbol, period="3mo", interval="1d")
    if data.empty or "Adj Close" not in data.columns:
        return None, None

    delta = data["Adj Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return data["Adj Close"], rsi

def render_rsi_bar(symbol: str):
    st.subheader("📊 RSI 條圖定位（30~70）")
    
    prices, rsi_series = fetch_rsi(symbol)
    if prices is None or rsi_series is None:
        st.error("❌ 無法取得 RSI 或價格資料")
        return

    current_price = round(prices[-1], 2)
    current_rsi = round(rsi_series[-1], 2)

    if pd.isna(current_price) or pd.isna(current_rsi):
        st.warning("⚠️ 資料尚未更新或計算失敗")
        return

    # 定義 RSI 30 與 70 的對應價格（簡單估算用線性外插）
    if len(prices) < 2 or len(rsi_series.dropna()) < 2:
        st.warning("⚠️ RSI 歷史資料不足")
        return

    recent_rsi = rsi_series.dropna().iloc[-20:]
    recent_prices = prices[-len(recent_rsi):]

    rsi_min = recent_rsi.min()
    rsi_max = recent_rsi.max()
    price_min = recent_prices.min()
    price_max = recent_prices.max()

    def map_rsi_to_price(target_rsi):
        # 線性對應估算
        if rsi_max == rsi_min:
            return current_price
        ratio = (target_rsi - rsi_min) / (rsi_max - rsi_min)
        return price_min + ratio * (price_max - price_min)

    price_rsi_30 = round(map_rsi_to_price(30), 2)
    price_rsi_70 = round(map_rsi_to_price(70), 2)

    fig = go.Figure()

    # 水平條
    fig.add_trace(go.Bar(
        x=[price_rsi_70 - price_rsi_30],
        y=["RSI"],
        base=price_rsi_30,
        orientation='h',
        marker=dict(color='lightblue'),
        hoverinfo='none',
        name="RSI 範圍"
    ))

    # 加上現價 marker
    fig.add_trace(go.Scatter(
        x=[current_price],
        y=["RSI"],
        mode='markers+text',
        marker=dict(color='red', size=12),
        text=[f"現價 {current_price}"],
        textposition="top center",
        name="現價"
    ))

    fig.update_layout(
        xaxis_title="價格",
        yaxis_title="",
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=20, r=20, t=30, b=30),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def run(symbol: str):
    render_rsi_bar(symbol)