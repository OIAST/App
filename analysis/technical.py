import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 6 個月日線資料
    end_date = datetime.today()
    start_date = end_date - timedelta(days=180)

    data = yf.download(
        symbol,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1d",
        progress=False
    )

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # ✅ 顯示資料範圍與筆數
    st.write(f"✅ 成功載入 {len(data)} 筆資料")
    st.write(f"日期範圍：{data.index.min().date()} ~ {data.index.max().date()}")

    # ✅ 顯示完整資料表
    st.dataframe(data)