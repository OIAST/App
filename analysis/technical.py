import yfinance as yf
import streamlit as st

def run(symbol):
    st.subheader(f"📊 技術分析 - {symbol}")

    try:
        data = yf.download(symbol, period="3mo", interval="1d")

        if data.empty:
            st.error("❌ 無法抓取資料，請確認股票代碼是否正確")
            return

        st.write("✅ 資料成功抓取")
        st.dataframe(data.head())

        # 額外確認 Volume 欄位狀況
        if "Volume" not in data.columns:
            st.warning("⚠️ 沒有 Volume 欄位")
        elif data["Volume"].isnull().sum() == len(data):
            st.warning("⚠️ Volume 全部為空值")
        else:
            st.success(f"✅ Volume 欄位存在，有 {data['Volume'].dropna().shape[0]} 筆有效資料")

    except Exception as e:
        st.error(f"❌ 錯誤發生：{e}")