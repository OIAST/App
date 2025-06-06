import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # ✅ 明確指定開始與結束日期（避免 yfinance 自動壓縮資料）
    end_date = datetime.today()
    start_date = end_date - timedelta(days=180)

    data = yf.download(
        symbol,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1d",
        progress=False
    )

    # 檢查資料是否成功取得
    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 檢查 Volume 欄位是否存在
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # ✅ 顯示前幾筆資料供確認
    st.write("✅ 資料成功載入，前幾筆如下：")
    st.dataframe(data.head())