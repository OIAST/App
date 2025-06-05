import streamlit as st
import pandas as pd

def run(symbol, data):
    st.subheader("📊 技術指標：Z-score 成交量")

    try:
        # ✅ 計算移動平均與標準差
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()

        # ✅ 避免 KeyError
        required_cols = ["Volume", "volume_ma20", "volume_std20"]
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            st.warning(f"⚠️ 欄位遺失：{missing}")
            return

        # ✅ 避免 ValueError（NaN 導致 z-score 無法計算）
        data = data.dropna(subset=required_cols).copy()
        if data.empty:
            st.warning("⚠️ 沒有足夠的有效資料來計算 Z-score")
            return

        # ✅ 計算 z-score
        data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
        st.line_chart(data["zscore_volume"])

    except Exception as e:
        st.error(f"❌ 錯誤發生：{e}")