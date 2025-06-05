import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def run(symbol: str):
    st.subheader("📊 成交量異常檢定（Z-score）")

    # 下載資料
    data = yf.download(symbol, period="6mo", interval="1d")

    if data is None or data.empty or "Volume" not in data.columns:
        st.error("❌ 無法下載股價資料或成交量資料缺失")
        return

    # 安全建立欄位
    try:
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()
    except Exception as e:
        st.error(f"❌ 計算移動平均時錯誤: {e}")
        return

    # 檢查欄位存在且不為空
    if not all(col in data.columns for col in ["volume_ma20", "volume_std20"]):
        st.error("❌ 缺少必要欄位 volume_ma20 或 volume_std20")
        return

    # 丟掉 NaN
    data = data.dropna(subset=["volume_ma20", "volume_std20"])
    if data.empty:
        st.error("❌ 無法計算異常值（有效資料不足）")
        return

    # 計算 Z-score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["anomaly"] = data["zscore_volume"].abs() > 2

    # 畫圖
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(data.index, data["Volume"], color="lightblue", label="成交量")
    ax.scatter(
        data[data["anomaly"]].index,
        data[data["anomaly"]]["Volume"],
        color="red", label="異常", zorder=5
    )
    ax.set_title(f"{symbol} 成交量異常 Z-score (> 2)")
    ax.set_ylabel("Volume")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)