import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def format_volume(val):
    """將數值自動縮寫，例如：23000 ➜ 2.3萬"""
    if pd.isna(val):
        return "-"
    if val >= 1_0000:
        return f"{val / 10000:.1f}萬"
    return str(int(val))


def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取一年資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算 20MA 與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 Z-score（需處理除以 0 的狀況）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["zscore_volume"] = data["zscore_volume"].replace([float("inf"), float("-inf")], pd.NA)

    # 顯示表格（縮寫 Volume）
    display_df = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_df["Volume"] = display_df["Volume"].apply(format_volume)
    display_df["volume_ma20"] = display_df["volume_ma20"].apply(format_volume)
    display_df["volume_std20"] = display_df["volume_std20"].apply(format_volume)
    display_df["zscore_volume"] = display_df["zscore_volume"].round(2)

    st.write("📋 近期量能與 Z-score 表：")
    st.dataframe(display_df.tail(30))

    # 繪圖（Z-score 折線圖）
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data["zscore_volume"],
        mode="lines+markers",
        name="Z-Score (Volume)"
    ))
    fig.update_layout(
        title="Z-Score（成交量）",
        xaxis_title="日期",
        yaxis_title="Z-Score",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)