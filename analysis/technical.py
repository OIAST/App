import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def render_rsi_bar(symbol: str):
    st.subheader(f"{symbol} RSI 技術指標視覺化")

    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty:
        st.warning("無法取得股價資料")
        return

    # 計算 RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data["RSI"] = rsi

    if data["RSI"].dropna().empty:
        st.warning("RSI 資料不足，無法顯示圖表")
        return

    # 取得最近一筆 RSI 和股價
    latest_rsi = data["RSI"].dropna().iloc[-1]
    latest_price = data["Close"].iloc[-1]

    # 模擬 RSI 30 和 RSI 70 對應的價格（估算）
    rsi_30 = data[data["RSI"] <= 30]["Close"].mean()
    rsi_70 = data[data["RSI"] >= 70]["Close"].mean()
    if not rsi_30 or rsi_30 != rsi_30:
        rsi_30 = data["Close"].quantile(0.1)
    if not rsi_70 or rsi_70 != rsi_70:
        rsi_70 = data["Close"].quantile(0.9)

    # 建立圖表
    fig = go.Figure()

    # RSI 區間條
    fig.add_trace(go.Bar(
        x=[rsi_70 - rsi_30],
        base=rsi_30,
        orientation='h',
        marker=dict(color='lightblue'),
        name='RSI 區間'
    ))

    # 現價點
    fig.add_trace(go.Scatter(
        x=[latest_price],
        y=[0],
        mode='markers+text',
        marker=dict(color='red', size=12),
        text=[f"現價: ${latest_price:.2f}"],
        textposition='top center',
        name='現價'
    ))

    fig.update_layout(
        title=f"{symbol} RSI 區間條（RSI: {latest_rsi:.2f}）",
        xaxis_title="股價",
        yaxis=dict(visible=False),
        height=150,
        margin=dict(l=40, r=40, t=40, b=30),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)