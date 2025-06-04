import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
import yfinance as yf
import pandas as pd

def run(symbol):
    st.subheader("📊 基本面分析 - 資產負債表")

    period = st.radio("選擇資料頻率", ["年", "季"], horizontal=True)

    ticker_data = yf.Ticker(symbol)
    df = ticker_data.balance_sheet if period == "年" else ticker_data.quarterly_balance_sheet
    df = df.T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.fillna(0)
    df.index = df.index.strftime('%y')  # 年份簡寫，如 2025 -> '25'

    def simplify(x):
        if x >= 1e8:
            return f"{x/1e8:.1f}億"
        elif x >= 1e4:
            return f"{x/1e4:.1f}萬"
        else:
            return f"{x:.0f}"

    # 圖1：資產結構圖
    st.markdown("### 🏗 資產結構圖")
    total_assets = df.get("Total Assets", 0)
    total_liabilities = df.get("Total Liab", 0)
    shareholder_equity = df.get("Total Stockholder Equity", 0)

    fig1, ax1 = plt.subplots()
    ax1.stackplot(df.index, total_liabilities, shareholder_equity, labels=["負債", "股東權益"])
    ax1.set_title("資產結構圖")
    ax1.set_ylabel("金額")
    ax1.legend()
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: simplify(x)))
    st.pyplot(fig1)

    # 圖2：流動資產與非流動資產
    st.markdown("### 🔄 流動資產與非流動資產")
    current_assets = df.get("Total Current Assets", 0)
    noncurrent_assets = total_assets - current_assets

    fig2, ax2 = plt.subplots()
    ax2.plot(df.index, current_assets, label="流動資產", marker='o')
    ax2.plot(df.index, noncurrent_assets, label="非流動資產", marker='s')
    ax2.set_title("流動與非流動資產變化")
    ax2.legend()
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: simplify(x)))
    st.pyplot(fig2)

    # 圖3：財務比率圖
    st.markdown("### 📉 財務比率")
    current_liabilities = df.get("Total Current Liabilities", 1)
    debt_ratio = total_liabilities / total_assets
    current_ratio = current_assets / current_liabilities

    fig3, ax3 = plt.subplots()
    ax3.plot(df.index, debt_ratio, label="負債比", marker='o')
    ax3.plot(df.index, current_ratio, label="流動比", marker='s')
    ax3.set_title("負債比與流動比")
    ax3.legend()
    ax3.yaxis.set_major_formatter(ticker.PercentFormatter(1.0))
    st.pyplot(fig3)

    # 圖4：股東權益變動圖
    st.markdown("### 🧾 股東權益變動")
    fig4, ax4 = plt.subplots()
    ax4.plot(df.index, shareholder_equity, label="股東權益", color='purple', marker='D')
    ax4.set_title("股東權益變動")
    ax4.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: simplify(x)))
    st.pyplot(fig4)