import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

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

    df = df.T
    df.index = df.index.strftime('%y年') if period == "年" else [f"{d.year%100}Q{(d.month-1)//3+1}" for d in df.index]

    def short_num(n):
        if pd.isna(n): return ""
        if abs(n) >= 1e8:
            return f"{n/1e8:.1f}億"
        elif abs(n) >= 1e4:
            return f"{n/1e4:.1f}萬"
        else:
            return f"{n:.0f}"

    # 資產結構圖
    st.markdown("### 1. 資產結構圖（資產 = 負債 + 股東權益）")
    fig1, ax1 = plt.subplots()
    assets = df.get("Total Assets", 0)
    liabilities = df.get("Total Liab", 0)
    equity = df.get("Total Stockholder Equity", 0)
    ax1.bar(df.index, liabilities, label="負債")
    ax1.bar(df.index, equity, bottom=liabilities, label="股東權益")
    ax1.set_ylabel("單位：USD")
    ax1.set_title("資產結構")
    ax1.legend()
    st.pyplot(fig1)

    # 流動 vs 非流動資產
    st.markdown("### 2. 流動資產與非流動資產變化")
    fig2, ax2 = plt.subplots()
    current_assets = df.get("Total Current Assets", 0)
    non_current_assets = assets - current_assets
    ax2.plot(df.index, current_assets, label="流動資產", marker="o")
    ax2.plot(df.index, non_current_assets, label="非流動資產", marker="o")
    ax2.set_title("流動 vs 非流動資產")
    ax2.legend()
    st.pyplot(fig2)

    # 負債比與流動比
    st.markdown("### 3. 負債比與流動比")
    fig3, ax3 = plt.subplots()
    current_liab = df.get("Total Current Liabilities", 0)
    debt_ratio = liabilities / assets
    current_ratio = current_assets / current_liab
    ax3.plot(df.index, debt_ratio, label="負債比", marker="o")
    ax3.plot(df.index, current_ratio, label="流動比", marker="o")
    ax3.axhline(1, color="gray", linestyle="--", linewidth=0.5)
    ax3.set_title("負債比 vs 流動比")
    ax3.legend()
    st.pyplot(fig3)