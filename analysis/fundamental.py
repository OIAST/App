import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def run(symbol):
    st.subheader("📊 基本面分析 - 資產負債表")

    period = st.radio("選擇期間", ["年", "季"], horizontal=True)
    ticker = yf.Ticker(symbol)

    if period == "年":
        df = ticker.balance_sheet
    else:
        df = ticker.quarterly_balance_sheet

    if df.empty:
        st.warning("找不到財報資料")
        return

    # 轉置，並重設 index 格式
    df = df.T.copy()
    df = df.sort_index()

    if period == "年":
        df.index = df.index.strftime('%y')
    else:
        df.index = [f"{d.year%100}Q{(d.month - 1)//3 + 1}" for d in df.index]

    # 移除缺值列，避免 plot 錯誤
    df = df.dropna(subset=["Total Assets", "Total Liab", "Total Stockholder Equity", "Total Current Assets", "Total Current Liabilities"], how='any')

    # 資料欄位
    assets = df["Total Assets"]
    liabilities = df["Total Liab"]
    equity = df["Total Stockholder Equity"]
    current_assets = df["Total Current Assets"]
    current_liab = df["Total Current Liabilities"]
    non_current_assets = assets - current_assets

    # 1. 資產結構圖
    st.markdown("### 1. 資產結構圖（資產 = 負債 + 股東權益）")
    fig1, ax1 = plt.subplots()
    ax1.bar(df.index, liabilities, label="負債")
    ax1.bar(df.index, equity, bottom=liabilities, label="股東權益")
    ax1.set_title("資產結構")
    ax1.legend()
    st.pyplot(fig1)

    # 2. 流動與非流動資產變化
    st.markdown("### 2. 流動資產與非流動資產變化")
    fig2, ax2 = plt.subplots()
    ax2.plot(df.index, current_assets, label="流動資產", marker="o")
    ax2.plot(df.index, non_current_assets, label="非流動資產", marker="o")
    ax2.set_title("資產構成變化")
    ax2.legend()
    st.pyplot(fig2)

    # 3. 財務比率圖（負債比與流動比）
    st.markdown("### 3. 負債比與流動比")
    debt_ratio = liabilities / assets
    current_ratio = current_assets / current_liab
    fig3, ax3 = plt.subplots()
    ax3.plot(df.index, debt_ratio, label="負債比", marker="o")
    ax3.plot(df.index, current_ratio, label="流動比", marker="o")
    ax3.axhline(1, color="gray", linestyle="--", linewidth=0.5)
    ax3.set_title("財務比率變化")
    ax3.legend()
    st.pyplot(fig3)