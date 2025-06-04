import streamlit as st
import yfinance as yf
import pandas as pd

# 英文對應中文（簡化常見欄位，可擴充）
column_map = {
    "Total Assets": "總資產",
    "Total Liab": "總負債",
    "Cash": "現金",
    "Cash And Cash Equivalents": "現金及約當現金",
    "Net Income": "淨利",
    "Total Revenue": "營收",
    "Gross Profit": "毛利",
    "Operating Income": "營業利益",
    "Total Cash From Operating Activities": "營業活動現金流",
    "Capital Expenditures": "資本支出",
    "Free Cash Flow": "自由現金流",
    # 可持續擴增
}

def format_number(value):
    try:
        if abs(value) >= 1e8:
            return f"{value / 1e8:.2f}億"
        elif abs(value) >= 1e4:
            return f"{value / 1e4:.2f}萬"
        else:
            return f"{value:.0f}"
    except:
        return value

def translate_and_format(df: pd.DataFrame):
    df = df.copy()
    df.index = [column_map.get(i, i) for i in df.index]
    return df.applymap(format_number)

def run(symbol):
    st.subheader(f"📊 基本面分析：{symbol}")

    # 資料區間選擇（年報或季報）
    freq = st.radio("選擇報表頻率：", ("年度報表", "季度報表"), horizontal=True)

    ticker = yf.Ticker(symbol)

    # 擷取三大報表
    try:
        if freq == "年度報表":
            balance_sheet = ticker.balance_sheet
            income_stmt = ticker.financials
            cashflow_stmt = ticker.cashflow
        else:
            balance_sheet = ticker.quarterly_balance_sheet
            income_stmt = ticker.quarterly_financials
            cashflow_stmt = ticker.quarterly_cashflow
    except Exception as e:
        st.error(f"無法擷取財報資料：{e}")
        return

    # 報表選擇
    report = st.radio("選擇要顯示的報表：", ("資產負債表", "損益表", "現金流量表"), horizontal=True)

    def show_table(df: pd.DataFrame, title: str):
        if df.empty:
            st.warning(f"⚠️ {title} 無資料")
            return
        df_display = translate_and_format(df)
        df_display = df_display.T
        df_display.index.name = "日期"
        st.dataframe(df_display)

    if report == "資產負債表":
        show_table(balance_sheet, "資產負債表")
    elif report == "損益表":
        show_table(income_stmt, "損益表")
    elif report == "現金流量表":
        show_table(cashflow_stmt, "現金流量表")