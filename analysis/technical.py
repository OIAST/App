import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

def run(symbol):
    st.subheader(f"📊 技術面分析 - {symbol}")

    # 下載歷史股價資料
    try:
        df = yf.download(symbol, period="6mo", interval="1d")
        if df.empty:
            st.warning("⚠️ 無法取得股價資料，請確認股票代碼是否正確。")
            return
    except Exception as e:
        st.error(f"資料下載失敗：{e}")
        return

    # K 線圖
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="K線圖"
        )
    ])
    fig.update_layout(
        title="K 線圖（最近六個月）",
        xaxis_title="日期",
        yaxis_title="價格",
        xaxis_rangeslider_visible=False,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)