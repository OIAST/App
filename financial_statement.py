import streamlit as st
import yfinance as yf
import pandas as pd

key_items_balance = [
    "Total Assets",
    "Total Equity Gross Minority Interest"
]

key_items_revenue = [
    "Total Revenue",
    "Gross Profit",
    "Operating Income",
    "Net Income",
]

key_items_cashflow = [
    "Operating Cash Flow",
    "Investing Cash Flow",
    "Financing Cash Flow"
]

def format_number(x):
    try:
        if abs(x) >= 100000000:
            return f"{x/100000000:,.1f} 億"
        elif abs(x) >= 10000:
            return f"{x/10000:,.0f} 萬"
        else:
            return f"{x:,.0f}"
    except:
        return x


def launcher_1(symbol):
    period_type = st.radio(
        "選擇報表期間",
        ["年度 (Yearly)", "季度 (Quarterly)"],
        horizontal=True
    )
    if st.button("產出報表"): 
        ticker = yf.Ticker(symbol)
        if period_type == "年度 (Yearly)":
            fin_data = {
                "Income Statement": ticker.financials,
                "Balance Sheet": ticker.balance_sheet,
                "Cash Flow": ticker.cashflow
            }
        else:
            fin_data = {
                "Income Statement": ticker.quarterly_financials,
                "Balance Sheet": ticker.quarterly_balance_sheet,
                "Cash Flow": ticker.quarterly_cashflow
            }
        df = pd.concat(fin_data.values()).T
        df_balance = df[key_items_balance].dropna(axis=0, how="all")
        df_revenue = df[key_items_revenue].dropna(axis=0, how="all")
        df_cashflow = df[key_items_cashflow].dropna(axis=0, how="all")
        if all(col in df_balance.columns for col in ["Total Assets", "Total Equity Gross Minority Interest"]):
            total_liab = df_balance["Total Assets"] - df_balance["Total Equity Gross Minority Interest"]
            total_liab_percentage = ((df_balance["Total Assets"] - df_balance["Total Equity Gross Minority Interest"])/df_balance["Total Assets"])*100
            df_balance.insert(
                loc=1,
                column="Total Liabilities",
                value=total_liab
            )
            df_balance.insert(
                loc=3,
                column="Debt Ratio %",
                value=total_liab_percentage
            )
        df_formatted = df_balance.applymap(format_number)
        df_formatted_2 = df_revenue.applymap(format_number)
        df_formatted_3 = df_cashflow.applymap(format_number)
        if df_formatted.empty:
            st.warning("⚠️ 無法取得資料，可能是 Yahoo Finance 未提供。")
        else:
            st.dataframe(df_formatted)
            st.dataframe(df_formatted_2)
            st.dataframe(df_formatted_3)

def launcher_2(symbol):
    period_type = st.radio("選擇報表期間", ["年度 (Yearly)", "季度 (Quarterly)"], horizontal=True)
    if st.button("產出報表"):
        ticker = yf.Ticker(symbol)
        income = ticker.financials.T if period_type == "年度 (Yearly)" else ticker.quarterly_financials.T

        if "Gross Profit" in income.columns and "Total Revenue" in income.columns:
            income["Gross Margin (%)"] = (income["Gross Profit"] / income["Total Revenue"] * 100).round(2)
            latest = income["Gross Margin (%)"].iloc[0]      
            previous = income["Gross Margin (%)"].iloc[1]    
            change_pct = ((latest - previous) / previous * 100).round(2)

            st.metric(
                label="毛利率 (%)",
                value=f"{latest} %",
                delta=f"{change_pct} %",
                border=True
            )
        else:
            st.warning("⚠️ 無法取得毛利或營收資料，無法計算毛利率。")

        income = ticker.financials.T if period_type == "年度 (Yearly)" else ticker.quarterly_financials.T

        eps_col = None
        for col_name in ["Diluted EPS"]:
            if col_name in income.columns:
                eps_col = col_name
                break

        if eps_col:
            latest_eps = income[eps_col].iloc[0]      # 最新
            previous_eps = income[eps_col].iloc[1]    # 上一季 / 前一年

            # 計算變化百分比
            change_pct = ((latest_eps - previous_eps) / previous_eps * 100).round(2)

            # 顯示 metric
            st.metric(
                label="EPS",
                value=f"{latest_eps:.2f}",
                delta=f"{change_pct} %",
                border=True
            )
        else:
            st.warning("⚠️ 無法取得 EPS 資料。")