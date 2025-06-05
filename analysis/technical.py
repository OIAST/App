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

    # 計算 20MA 與 20STD
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 丟掉NA資料
    data = data.dropna(subset=["volume_ma20", "volume_std20"]).copy()

    if data.empty:
        st.warning("⚠️ 有效資料不足，請選更長的區間")
        return

    try:
        # 計算 Z-score（這裡不應再報錯）
        zscore = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
        data["zscore_volume"] = zscore
        data["anomaly"] = data["zscore_volume"].abs() > 2
    except Exception as e:
        st.error(f"❌ Z-score 計算錯誤: {e}")
        return

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