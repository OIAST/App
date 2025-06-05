import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def run(symbol: str):
    st.subheader("📊 成交量異常檢定（Z-score）")

    data = yf.download(symbol, period="6mo", interval="1d")

    if data is None or data.empty or "Volume" not in data.columns:
        st.error("❌ 無法下載股價資料或缺少成交量欄位")
        return

    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 安全 dropna
    expected_cols = ["volume_ma20", "volume_std20"]
    valid_cols = [col for col in expected_cols if col in data.columns]

    if len(valid_cols) < len(expected_cols):
        st.warning(f"⚠️ 缺少必要欄位：{set(expected_cols) - set(valid_cols)}，跳過 dropna 檢查。")
    else:
        data = data.dropna(subset=valid_cols)

    if data.empty:
        st.error("❌ 資料為空，無法進行後續分析")
        return

    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["anomaly"] = data["zscore_volume"].abs() > 2

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(data.index, data["Volume"], color="skyblue", label="成交量")
    ax.scatter(
        data[data["anomaly"]].index,
        data[data["anomaly"]]["Volume"],
        color="red", label="異常", zorder=5
    )
    ax.set_title(f"{symbol} 成交量異常（Z-score > 2）")
    ax.set_ylabel("Volume")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)