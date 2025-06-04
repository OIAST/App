import streamlit as st
import yfinance as yf
import pandas as pd

def run(symbol):
    st.subheader(f"📊 基本面分析：{symbol}")

    ticker = yf.Ticker(symbol)

    # 擷取三大財報
    try:
        balance_sheet = ticker.balance_sheet
        income_stmt = ticker.financials
        cashflow_stmt = ticker.cashflow
    except Exception as e:
        st.error(f"無法擷取財報資料：{e}")
        return

    # 按鈕選單
    option = st.radio(
        "選擇要顯示的報表：",
        ("資產負債表", "損益表", "現金流量表"),
        horizontal=True
    )

    # 顯示報表
    def show_table(df: pd.DataFrame, title: str):
        if df.empty:
            st.warning(f"⚠️ {title} 無資料")
            return
        df_display = df.T
        df_display.index.name = "日期"
        st.dataframe(df_display)

    if option == "資產負債表":
        show_table(balance_sheet, "資產負債表")
    elif option == "損益表":
        show_table(income_stmt, "損益表")
    elif option == "現金流量表":
        show_table(cashflow_stmt, "現金流量表")