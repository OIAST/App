import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter

# 設定中文字型避免亂碼
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def format_number(x, pos):
    if abs(x) >= 1e8:
        return f'{x/1e8:.0f}億'
    elif abs(x) >= 1e4:
        return f'{x/1e4:.0f}萬'
    else:
        return f'{x:.0f}'

def run(symbol):
    st.subheader("📊 財務報表分析")
    period_type = st.radio("選擇期間類型", ["年", "季"], horizontal=True)
    report_type = st.radio("選擇報表類型", ["資產負債表", "損益表", "現金流量表"], horizontal=True)

    ticker = yf.Ticker(symbol)

    if period_type == "季":
        balance = ticker.quarterly_balance_sheet
        income = ticker.quarterly_financials
        cashflow = ticker.quarterly_cashflow
    else:
        balance = ticker.balance_sheet
        income = ticker.financials
        cashflow = ticker.cashflow

    if balance.empty:
        st.warning("⚠️ 無法取得財報資料，請確認股票代碼或稍後再試。")
        return

    # 調整資料方向
    df = balance.T if report_type == "資產負債表" else income.T if report_type == "損益表" else cashflow.T

    # 轉換 index 為 '23Q1' 或 '23'
    if period_type == "季":
        df.index = [f"{str(d.year)[2:]}Q{((d.month - 1)//3 + 1)}" for d in df.index]
    else:
        df.index = [str(d.year)[2:] for d in df.index]

    st.markdown(f"### {report_type}：{symbol.upper()}")

    if report_type == "資產負債表":
        col1, col2 = st.columns(2)

        # 1️⃣ 資產結構圖
        with col1:
            st.markdown("#### 1. 資產結構（資產 = 負債 + 股東權益）")
            assets = df.get("Total Assets")
            liabilities = df.get("Total Liab")
            equity = df.get("Total Stockholder Equity")

            if assets is not None and liabilities is not None and equity is not None:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(df.index, assets, label="總資產", marker='o')
                ax.plot(df.index, liabilities, label="總負債", marker='o')
                ax.plot(df.index, equity, label="股東權益", marker='o')
                ax.yaxis.set_major_formatter(FuncFormatter(format_number))
                ax.set_ylabel("金額")
                ax.set_xlabel("期間")
                ax.legend()
                st.pyplot(fig)

        # 2️⃣ 流動資產與非流動資產
        with col2:
            st.markdown("#### 2. 資產分類變化")
            current_assets = df.get("Total Current Assets")
            noncurrent_assets = assets - current_assets if (assets is not None and current_assets is not None) else None

            if current_assets is not None and noncurrent_assets is not None:
                fig, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(df.index, current_assets, label="流動資產", marker='o')
                ax2.plot(df.index, noncurrent_assets, label="非流動資產", marker='o')
                ax2.yaxis.set_major_formatter(FuncFormatter(format_number))
                ax2.set_ylabel("金額")
                ax2.set_xlabel("期間")
                ax2.legend()
                st.pyplot(fig)

        # 3️⃣ 負債比與流動比
        st.markdown("#### 3. 財務比率")
        current_liabilities = df.get("Total Current Liabilities")
        total_assets = df.get("Total Assets")
        total_liabilities = df.get("Total Liab")

        if current_assets is not None and current_liabilities is not None and total_assets is not None and total_liabilities is not None:
            debt_ratio = (total_liabilities / total_assets) * 100
            current_ratio = (current_assets / current_liabilities)

            fig, ax3 = plt.subplots(figsize=(8, 4))
            ax3.plot(df.index, debt_ratio, label="負債比 (%)", marker='o')
            ax3.plot(df.index, current_ratio, label="流動比", marker='o')
            ax3.set_ylabel("比例")
            ax3.set_xlabel("期間")
            ax3.legend()
            st.pyplot(fig)

    else:
        st.dataframe(df.style.format("{:,.0f}"))