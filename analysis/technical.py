import streamlit as st
import pandas as pd

def run(symbol: str, data: pd.DataFrame):
    st.subheader(f"📊 技術面分析 - {symbol}")

    # 檢查 Volume 是否存在
    if "Volume" not in data.columns:
        st.error("❌ 無法進行分析，資料缺少 Volume 欄位")
        st.dataframe(data.head())
        return

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    missing_cols = [col for col in required_cols if col not in data.columns]

    if missing_cols:
        st.warning(f"⚠️ 缺少必要欄位：{missing_cols}")
        return

    # 避免 NaN 錯誤
    data_clean = data.dropna(subset=required_cols).copy()
    if data_clean.empty:
        st.warning("⚠️ 無法計算 z-score，可能是資料不足")
        return

    # 計算 Z-score
    data_clean["zscore_volume"] = (
        (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]
    )

    # 顯示結果
    st.line_chart(data_clean[["Volume", "volume_ma20"]])
    st.line_chart(data_clean["zscore_volume"])