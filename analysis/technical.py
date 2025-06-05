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
            st.error("❌ 沒有成交量資料 (Volume)")
            st.write("實際欄位：", list(data.columns))
            return

        # 計算移動平均與標準差
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()

        # 檢查欄位是否真的建立成功
        if "volume_ma20" not in data.columns or "volume_std20" not in data.columns:
            st.error("❌ volume_ma20 或 volume_std20 欄位未成功建立")
            return

        # 顯示有 NaN 的狀態給你確認
        nan_stats = data[["Volume", "volume_ma20", "volume_std20"]].isna().sum()
        st.write("❕ NaN 檢查：", nan_stats.to_dict())

        # 過濾掉 NaN
        data = data.dropna(subset=["volume_ma20", "volume_std20"])
        if data.empty:
            st.warning("⚠️ 所有資料都是 NaN，無法分析")
            return

        # 計算 z-score
        data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
        if data["zscore_volume"].isna().all():
            st.error("❌ Z-Score 計算結果為全 NaN")
            return

        # 顯示結果表格
        st.dataframe(data[["Close", "Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(10))

        # 畫圖
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["zscore_volume"], name="Z-Score"))
        fig.add_trace(go.Scatter(x=data.index, y=[2]*len(data), name="+2σ", line=dict(dash='dash', color='red')))
        fig.add_trace(go.Scatter(x=data.index, y=[-2]*len(data), name="-2σ", line=dict(dash='dash', color='blue')))
        fig.update_layout(title=f"{symbol} 成交量異常 Z-Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("❌ 程式發生錯誤")
        st.exception(e)