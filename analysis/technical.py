import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

def render_rsi_bar(symbol: str):
    stock = yf.Ticker(symbol)
    df = stock.history(period="3mo", interval="1d")

    if df.empty:
        st.warning("無法取得股價資料")
        return

    close = df["Close"]
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    latest_rsi = round(rsi.iloc[-1], 2)
    current_price = round(close.iloc[-1], 2)

    low_rsi_price = close[rsi <= 30].min()
    high_rsi_price = close[rsi >= 70].max()

    low_rsi_price = round(low_rsi_price, 2) if not pd.isna(low_rsi_price) else current_price * 0.9
    high_rsi_price = round(high_rsi_price, 2) if not pd.isna(high_rsi_price) else current_price * 1.1

    fig = go.Figure()

    # 建立條狀圖
    fig.add_trace(go.Bar(
        x=["RSI 價格區間"],
        y=[high_rsi_price - low_rsi_price],
        base=low_rsi_price,
        marker=dict(color="lightgray"),
        name="RSI 區間"
    ))

    # 加入目前價格的標示線
    fig.add_trace(go.Scatter(
        x=["RSI 價格區間"],
        y=[current_price],
        mode="markers+text",
        marker=dict(color="red", size=10),
        text=[f"目前價格：{current_price}"],
        textposition="top center",
        name="目前價格"
    ))

    fig.update_layout(
        title=f"{symbol} RSI 條狀圖（目前 RSI: {latest_rsi}）",
        yaxis_title="價格",
        bargap=0.3,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def run(symbol: str):
    st.header("📊 技術分析")
    render_rsi_bar(symbol)