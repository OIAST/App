import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def fuzzy_find(columns, target_keywords):
    """模糊匹配欄位名稱"""
    for keyword in target_keywords:
        for col in columns:
            if keyword.lower() in col.lower():
                return col
    return None

def simplify_number(n):
    """簡化數字顯示（萬、百萬、十億）"""
    if abs(n) >= 1e9:
        return f"{n/1e9:.1f}B"
    elif abs(n) >= 1e6:
        return f"{n/1e6:.1f}M"
    elif abs(n) >= 1e4:
        return f"{n/1e4:.1f}W"
    else:
        return str(round(n, 2))

def run(symbol):
    st.header("📊 資產負債表分析")

    period_type = st.radio("選擇資料頻率", ["年度", "季"], horizontal=True)
    is_annual = period_type == "年度"

    stock = yf.Ticker(symbol)
    df = stock.balance_sheet if is_annual else stock.quarterly_balance_sheet

    if df.empty:
        st.warning("⚠️ 無法取得財報資料，請確認股票代碼或稍後再試。")
        return

    df = df.T.sort_index()
    df.index = df.index.strftime('%y' if is_annual else '%yQ%q')  # 顯示如 23 或 23Q1

    # 模糊抓欄位
    total_assets_col = fuzzy_find(df.columns, ["Total Assets"])
    total_liab_col = fuzzy_find(df.columns, ["Total Liabilities", "Total Liab"])
    equity_col = fuzzy_find(df.columns, ["Stockholder Equity", "Shareholders' Equity"])
    current_assets_col = fuzzy_find(df.columns, ["Current Assets"])
    current_liab_col = fuzzy_find(df.columns, ["Current Liabilities"])

    # 有任一欄位抓不到就顯示錯誤
    required = [total_assets_col, total_liab_col, equity_col, current_assets_col, current_liab_col]
    if None in required:
        st.error("❌ 某些必要財報欄位未找到，無法顯示圖表。")
        st.write("嘗試找到的欄位：", {
            "Total Assets": total_assets_col,
            "Total Liabilities": total_liab_col,
            "Equity": equity_col,
            "Current Assets": current_assets_col,
            "Current Liabilities": current_liab_col,
        })
        return

    # 移除空值資料
    df = df[[total_assets_col, total_liab_col, equity_col, current_assets_col, current_liab_col]].dropna()

    # 圖表 1：資產結構（總資產、負債、股東權益）
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df[total_assets_col], label="總資產", marker="o")
    ax.plot(df.index, df[total_liab_col], label="負債", marker="o")
    ax.plot(df.index, df[equity_col], label="股東權益", marker="o")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: simplify_number(x)))
    ax.set_title("資產結構")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 圖表 2：流動資產與負債
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(df.index, df[current_assets_col], label="流動資產", marker="o")
    ax2.plot(df.index, df[current_liab_col], label="流動負債", marker="o")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: simplify_number(x)))
    ax2.set_title("流動資產與負債")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    # 圖表 3：負債比與流動比
    df["負債比率"] = df[total_liab_col] / df[total_assets_col] * 100
    df["流動比率"] = df[current_assets_col] / df[current_liab_col] * 100
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(df.index, df["負債比率"], label="負債比率 %", marker="o")
    ax3.plot(df.index, df["流動比率"], label="流動比率 %", marker="o")
    ax3.set_title("負債與流動比率")
    ax3.legend()
    ax3.grid(True)
    st.pyplot(fig3)