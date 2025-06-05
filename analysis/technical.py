# analysis/technical.py
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

def run(symbol):
    st.subheader("📊 技術面分析 - 成交量異常偵測")

    try:
        # 下載資料
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if data.empty:
            st.error("❌ 無法下載資料，請確認股票代碼")
            return

        if "Volume" not in data.columns:
            st.error("❌ 沒有成交量資料")
            return

        # 計算 volume_ma20 與 volume_std20
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()

        # 安全檢查欄位是否存在
        missing_cols = [col for col in ["volume_ma20", "volume_std20"] if col not in data.columns]
        if missing_cols:
            st.error(f"⚠️ 欄位遺失：{missing_cols}")
            st.write("目前欄位：", data.columns.tolist())
            return

        # 移除 NaN 資料：但前提是欄位真的有存在
        subset_cols = [col for col in ["volume_ma20", "volume_std20"] if col in data.columns]
        data = data.dropna(subset=subset_cols)
        if data.empty:
            st.warning("⚠️ 無足夠資料進行分析（可能是前20天都被 drop 掉）")
            return

        # 計算 z-score，這邊改用 .get 確保欄位存在
        data["zscore_volume"] = (
            (data["Volume"] - data.get("volume_ma20", 0)) / data.get("volume_std20", 1)
        )

        # 顯示結果
        st.dataframe(data[["Close", "Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(10))

        # 繪圖
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["zscore_volume"], name="Z-Score"))
        fig.add_trace(go.Scatter(x=data.index, y=[2]*len(data), name="+2σ", line=dict(dash='dash', color='red')))
        fig.add_trace(go.Scatter(x=data.index, y=[-2]*len(data), name="-2σ", line=dict(dash='dash', color='blue')))
        fig.update_layout(title=f"{symbol} 成交量異常 Z-Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("❌ 發生錯誤")
        st.exception(e)