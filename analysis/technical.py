import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def run(symbol: str):
    st.subheader("📊 成交量異常檢定（Z-score）")

    # 擷取資料
    data = yf.download(symbol, period="6mo", interval="1d")

    if data is None or data.empty or "Volume" not in data.columns:
        st.error("❌ 無法下載股價資料或成交量資料缺失")
        return

    # 計算20日平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 去除NaN避免錯誤
    data = data.dropna(subset=["volume_ma20", "volume_std20"])

    # 確認數據長度足夠
    if data.empty:
        st.error("❌ 資料不足，無法進行統計檢定")
        return

    # 計算Z-score與異常點
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["anomaly"] = data["zscore_volume"].abs() > 2

    # 繪圖
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