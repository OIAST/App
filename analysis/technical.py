import yfinance as yf
import streamlit as st

def run(symbol):
    st.subheader(f"📊 技術分析 - {symbol}")

    try:
        data = yf.download(symbol, period="3mo", interval="1d")

        if data.empty:
            st.error("❌ 無法抓取資料，請確認股票代碼是否正確")
            return

        st.write("✅ 資料成功抓取，前幾筆如下：")
        st.dataframe(data.head())

        # ✅ Volume 欄位檢查
        if "Volume" not in data.columns:
            st.warning("⚠️ 沒有 Volume 欄位")
        elif data["Volume"].isnull().all():
            st.warning("⚠️ Volume 欄位全部為空值")
        else:
            valid_count = data["Volume"].notnull().sum()
            st.success(f"✅ Volume 欄位存在，有 {valid_count} 筆有效資料")

    except Exception as e:
        st.error(f"❌ 錯誤發生：{e}")