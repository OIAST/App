import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def render_rsi_bar(symbol: str):
    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty or "Close" not in data.columns:
        st.warning("找不到股票資料或收盤價資料缺失")
        return

    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    data["RSI"] = rsi
    current_price = data["Close"].iloc[-1]

    if pd.isna(current_price) or current_price == 0:
        st.warning("目前價格為空，無法產生 RSI 分析")
        return

    # 取得 RSI 30 與 70 對應的價格中位數
    low_rsi_price = data[data["RSI"] <= 30]["Close"].median()
    high_rsi_price = data[data["RSI"] >= 70]["Close"].median()

    # 若無有效數據，使用估算值
    if pd.isna(low_rsi_price) or low_rsi_price == 0:
        low_rsi_price = round(current_price * 0.9, 2)
    if pd.isna(high_rsi_price) or high_rsi_price == 0:
        high_rsi_price = round(current_price * 1.1, 2)

    # 建立 RSI 區間 bar 圖
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["RSI區間"],
        y=[high_rsi_price - low_rsi_price],
        base=low_rsi_price,
        marker=dict(color="#e0e0e0"),
        name="RSI 30~70 區間",
        hoverinfo="none",
    ))

    fig.add_trace(go.Scatter(
        x=["RSI區間"],
        y=[current_price],
        mode="markers+text",
        marker=dict(color="red", size=14),
        text=[f"現價 {current_price:.2f}"],
        textposition="top center",
        name="現價",
    ))

    fig.update_layout(
        height=250,
        title="📉 RSI 價格區間（30~70）與現價位置",
        yaxis_title="股價",
        xaxis_showticklabels=False,
        bargap=0.4,
        margin=dict(t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def run(symbol: str):
    st.subheader("技術指標：RSI 價格區間")
    render_rsi_bar(symbol)