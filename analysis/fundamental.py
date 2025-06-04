import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from rapidfuzz import fuzz, process

# 進階模糊比對欄位
def fuzzy_match_column(columns, target_keywords, threshold=70):
    best_match = None
    best_score = 0
    for keyword in target_keywords:
        result = process.extractOne(keyword, columns, scorer=fuzz.token_sort_ratio)
        if result and result[1] > best_score and result[1] >= threshold:
            best_match = result[0]
            best_score = result[1]
    return best_match

# 數值轉換 例如 10000 -> 1W
def convert_number(n):
    if abs(n) >= 1e8:
        return f"{n / 1e8:.1f}億"
    elif abs(n) >= 1e4:
        return f"{n / 1e4:.1f}萬"
    else:
        return f"{n:.0f}"

def run(symbol):
    st.subheader("📊 基本面分析：資產負債表")

    period_type = st.radio("選擇財報類型", ["季報", "年報"], horizontal=True)
    is_annual = period_type == "年報"

    st.markdown("資料來源：Yahoo Finance")

    ticker = yf.Ticker(symbol)

    try:
        df = ticker.quarterly_balance_sheet if not is_annual else ticker.balance_sheet
        df = df.transpose()
    except Exception as e:
        st.error("❌ 無法下載財報資料，請檢查股票代碼。")
        return

    if df.empty:
        st.warning("⚠️ 無財報資料可顯示。")
        return

    # 嘗試模糊搜尋欄位
    columns = list(df.columns)
    assets_col = fuzzy_match_column(columns, ["Total Assets"])
    liabilities_col = fuzzy_match_column(columns, ["Total Liabilities"])
    equity_col = fuzzy_match_column(columns, ["Total Stockholder Equity", "Equity"])
    current_assets_col = fuzzy_match_column(columns, ["Total Current Assets"])
    current_liabilities_col = fuzzy_match_column(columns, ["Total Current Liabilities"])

    found = {
        "Total Assets": assets_col,
        "Total Liabilities": liabilities_col,
        "Equity": equity_col,
        "Current Assets": current_assets_col,
        "Current Liabilities": current_liabilities_col,
    }

    if None in found.values():
        st.error("❌ 某些必要財報欄位未找到，無法顯示圖表。")
        st.json(found)
        return

    # 數據處理
    df = df[[assets_col, liabilities_col, equity_col, current_assets_col, current_liabilities_col]].dropna()
    df = df.iloc[::-1]  # 時間由舊到新
    df.index = df.index.to_series().dt.strftime('%yQ%q') if not is_annual else df.index.to_series().dt.strftime('%y')

    # 資產結構圖
    st.markdown("### 🏛️ 資產結構（總資產 = 負債 + 股東權益）")
    fig1, ax1 = plt.subplots()
    ax1.plot(df.index, df[assets_col], label="總資產", marker='o')
    ax1.plot(df.index, df[liabilities_col], label="總負債", marker='o')
    ax1.plot(df.index, df[equity_col], label="股東權益", marker='o')
    ax1.legend()
    ax1.set_title("資產結構")
    ax1.set_ylabel("金額")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # 流動資產 vs 非流動資產（簡化為總資產 - 流動資產）
    st.markdown("### 🔄 流動資產與非流動資產變化")
    fig2, ax2 = plt.subplots()
    current_assets = df[current_assets_col]
    non_current_assets = df[assets_col] - current_assets
    ax2.plot(df.index, current_assets, label="流動資產", marker="o")
    ax2.plot(df.index, non_current_assets, label="非流動資產", marker="o")
    ax2.legend()
    ax2.set_title("資產結構細分")
    ax2.set_ylabel("金額")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 負債比與流動比
    st.markdown("### ⚖️ 財務比率：負債比與流動比")
    df["負債比"] = df[liabilities_col] / df[assets_col]
    df["流動比"] = df[current_assets_col] / df[current_liabilities_col]
    fig3, ax3 = plt.subplots()
    ax3.plot(df.index, df["負債比"], label="負債比", marker="o")
    ax3.plot(df.index, df["流動比"], label="流動比", marker="o")
    ax3.legend()
    ax3.set_title("財務比率")
    ax3.set_ylabel("比率")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # 顯示最新一筆數據表格
    st.markdown("### 📄 最新財報摘要")
    latest_row = df.iloc[-1].copy()
    summary = {
        "總資產": convert_number(latest_row[assets_col]),
        "總負債": convert_number(latest_row[liabilities_col]),
        "股東權益": convert_number(latest_row[equity_col]),
        "流動資產": convert_number(latest_row[current_assets_col]),
        "流動負債": convert_number(latest_row[current_liabilities_col]),
        "負債比": f"{latest_row['負債比']:.2%}",
        "流動比": f"{latest_row['流動比']:.2f}",
    }
    st.table(pd.DataFrame(summary.items(), columns=["項目", "數值"]))