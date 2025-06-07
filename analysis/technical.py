import yfinance as yf
import pandas as pd
import streamlit as st

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取 90 天資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或缺少 Volume 欄位")
        return

    # 確保 Volume 是數字格式
    data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 計算 z-score（這裡保持簡單邏輯）
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

    # 顯示欄位資料型態
    st.write("### 欄位資料型態 (dtype)")
    st.code(f"""
Volume:         {data["Volume"].dtype}
volume_ma20:    {data["volume_ma20"].dtype}
volume_std20:   {data["volume_std20"].dtype}
zscore_volume:  {data["zscore_volume"].dtype}
    """)

    # 顯示前 10 筆資料（含 NaN）
    st.write("### 前 10 筆數據預覽")
    st.dataframe(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].head(10))