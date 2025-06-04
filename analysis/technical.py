import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

def run(symbol):
    st.subheader(f"技術分析：{symbol}")

    # 抓取資料
    df = yf.download(symbol, interval="1d", period="3mo", progress=False)

    # 若資料為空
    if df.empty or "Close" not in df.columns:
        st.warning("⚠️ 無法取得股價資料，請確認股票代碼是否正確或目前有交易記錄。")
        return

    # 若價格欄為 NaN 或 0，視為無效
    if df["Close"].isnull().all() or (df["Close"] == 0).all():
        st.warning("⚠️ 資料有誤：收盤價格無有效資料。")
        st.dataframe(df)  # 顯示原始資料方便除錯
        return

    # 畫 K 線圖
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
        title=f"{symbol} 近期 K 線圖",
        xaxis_title="日期",
        yaxis_title="價格（USD）",
        autosize=False,
        width=720,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=False)