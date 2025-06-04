import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches

# 進階欄位對應函數
def fuzzy_find(column_candidates, keywords):
    found = {}
    for key, kw_list in keywords.items():
        match = None
        for kw in kw_list:
            match = get_close_matches(kw.lower(), [c.lower() for c in column_candidates], n=1, cutoff=0.7)
            if match:
                found[key] = next((c for c in column_candidates if c.lower() == match[0]), None)
                break
        if key not in found:
            found[key] = None
    return found

# 數值縮寫顯示
def format_number(val):
    if abs(val) >= 1e8:
        return f"{val/1e8:.1f}億"
    elif abs(val) >= 1e4:
        return f"{val/1e4:.1f}萬"
    else:
        return f"{val:.0f}"

def run(symbol):
    st.header("📊 基本面分析 - 資產負債表")
    
    # 年 or 季
    freq = st.radio("選擇財報頻率", ["年度", "季度"], horizontal=True)
    is_annual = freq == "年度"
    
    ticker = yf.Ticker(symbol)
    df = ticker.balance_sheet if is_annual else ticker.quarterly_balance_sheet
    if df.empty:
        st.warning("找不到財報資料")
        return
    
    df = df.T.sort_index()
    df.index = df.index.strftime("%y") if is_annual else df.index.strftime("%yQ%q")
    columns = df.columns.tolist()

    keywords = {
        "Total Assets": ["total assets"],
        "Total Liabilities": ["total liabilities", "total liab"],
        "Equity": ["total stockholder equity", "equity", "shareholders equity"],
        "Current Assets": ["total current assets", "current assets"],
        "Current Liabilities": ["total current liabilities", "current liabilities"]
    }
    matched = fuzzy_find(columns, keywords)

    # 檢查是否都成功匹配
    if None in matched.values():
        st.error("❌ 某些必要財報欄位未找到，無法顯示圖表。")
        st.json(matched)
        return
    
    df_filtered = df[[v for v in matched.values() if v]]
    df_filtered = df_filtered.dropna()

    # 圖表 1：資產結構（資產=負債+股東權益）
    st.subheader("資產結構")
    fig1, ax1 = plt.subplots()
    ax1.plot(df_filtered.index, df_filtered[matched["Total Assets"]], label="資產", marker="o")
    ax1.plot(df_filtered.index, df_filtered[matched["Total Liabilities"]], label="負債", marker="o")
    ax1.plot(df_filtered.index, df_filtered[matched["Equity"]], label="股東權益", marker="o")
    ax1.legend()
    ax1.set_ylabel("金額")
    ax1.set_title("資產 vs 負債 vs 權益")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # 圖表 2：流動 vs 非流動資產
    st.subheader("流動與非流動資產變化")
    current_assets = df_filtered[matched["Current Assets"]]
    non_current_assets = df_filtered[matched["Total Assets"]] - current_assets
    fig2, ax2 = plt.subplots()
    ax2.plot(df_filtered.index, current_assets, label="流動資產", marker="o")
    ax2.plot(df_filtered.index, non_current_assets, label="非流動資產", marker="o")
    ax2.legend()
    ax2.set_title("資產結構變化")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 圖表 3：負債比與流動比
    st.subheader("財務比率")
    debt_ratio = df_filtered[matched["Total Liabilities"]] / df_filtered[matched["Total Assets"]]
    current_ratio = df_filtered[matched["Current Assets"]] / df_filtered[matched["Current Liabilities"]]
    fig3, ax3 = plt.subplots()
    ax3.plot(df_filtered.index, debt_ratio, label="負債比", marker="o")
    ax3.plot(df_filtered.index, current_ratio, label="流動比", marker="o")
    ax3.legend()
    ax3.set_title("負債比 vs 流動比")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # 最新資料摘要
    st.subheader("📋 最新財報摘要")
    latest = df_filtered.iloc[-1]
    data_summary = {
        "資產": format_number(latest[matched["Total Assets"]]),
        "負債": format_number(latest[matched["Total Liabilities"]]),
        "權益": format_number(latest[matched["Equity"]]),
        "流動資產": format_number(latest[matched["Current Assets"]]),
        "流動負債": format_number(latest[matched["Current Liabilities"]]),
    }
    st.table(pd.DataFrame(data_summary.items(), columns=["項目", "金額"]))