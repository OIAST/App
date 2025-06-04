import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

def run(symbol):
    st.subheader(f"技術分析：{symbol}")
    
    df = yf.download(symbol, interval="1d", period="3mo")

    if df.empty:
        st.warning("無法取得股價資料，請確認股票代碼是否正確")
        return

    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="K 線"
        )
    ])

    fig.update_layout(
        title=f"{symbol} K 線圖（近 3 個月）",
        xaxis_title="日期",
        yaxis_title="價格（USD）",
        width=900,
        height=500
    )

    st.plotly_chart(fig, use_container_width=False)