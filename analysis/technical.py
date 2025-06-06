import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 1. 抓取 6 個月日線資料
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    # 資料檢查
    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 2. 計算 Volume 的移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 3. 計算 Z-score（含錯誤防呆）
    mask = data["volume_std20"].notnull() & (data["volume_std20"] != 0)
    data.loc[mask, "zscore_volume"] = (
        (data.loc[mask, "Volume"] - data.loc[mask, "volume_ma20"]) / data.loc[mask, "volume_std20"]
    )

    # 4. 顯示指標資料
    st.write("✅ 前 30 筆計算結果：")
    st.dataframe(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].tail(30))

    # 5. 顯示原始資料
    with st.expander("📄 查看完整原始資料"):
        st.dataframe(data.tail(100))