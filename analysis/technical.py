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

    # 避免重複執行造成欄位名稱不存在錯誤
    if "volume_ma20" not in data.columns:
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    if "volume_std20" not in data.columns:
        data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 再次確認欄位建立成功
    if "volume_ma20" not in data.columns or "volume_std20" not in data.columns:
        st.error("❌ 無法計算移動平均與標準差")
        return

    # 先 dropna（但加上欄位是否存在的檢查）
    valid_cols = [col for col in ["volume_ma20", "volume_std20"] if col in data.columns]
    data = data.dropna(subset=valid_cols)

    if data.empty:
        st.warning("⚠️ 資料不足，請選擇更長的時間區間")
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