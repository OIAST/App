import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 1. 抓資料（6個月）
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 2. 計算 Volume 的移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 3. 計算 Z-score：成交量偏離程度
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 4. 顯示資訊確認
    st.write(f"✅ 共 {len(data)} 筆資料")
    st.write(f"日期範圍：{data.index.min().date()} ～ {data.index.max().date()}")
    st.dataframe(data.tail(10))  # 顯示最後10筆

    # 5. 畫圖：Z-score Volume
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["zscore_volume"],
                             mode="lines", name="Z-score Volume"))
    fig.update_layout(title="Z-score Volume（20日）",
                      xaxis_title="日期", yaxis_title="Z-score",
                      height=400)
    st.plotly_chart(fig, use_container_width=True)