import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol):
    st.subheader(f"📊 技術面分析（成交量）：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 計算 20 日移動平均與標準差
    data["Volume"] = data["Volume"].fillna(0).astype(int)
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 顯示原始數據表格（近 30 筆）
    display_data = data[["Volume", "volume_ma20", "volume_std20"]].copy()
    st.write("📋 成交量統計數據（近 30 日）")
    st.dataframe(display_data.tail(30))

    # 畫成交量與移動平均圖表
    st.write("📈 成交量趨勢圖（含 20 日均量）")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Volume", marker_color="lightblue"))
    fig.add_trace(go.Scatter(x=data.index, y=data["volume_ma20"], name="20日均量", line=dict(color="orange", width=2)))
    fig.add_trace(go.Scatter(x=data.index, y=data["volume_std20"], name="20日標準差", line=dict(color="green", dash="dot")))

    fig.update_layout(
        height=500,
        xaxis_title="日期",
        yaxis_title="成交量",
        legend_title="指標",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)