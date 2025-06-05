import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def run(symbol: str):
    st.subheader("📊 成交量異常檢定（Z-score）")

    # 抓取資料
    data = yf.download(symbol, period="6mo", interval="1d")

    if data is None or data.empty or "Volume" not in data.columns:
        st.error("❌ 無法下載股價資料或缺少成交量欄位")
        return

    # 建立移動平均與標準差欄位（會產生 NaN 開頭）
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 只對實際存在的欄位進行 dropna
    valid_cols = [col for col in ["volume_ma20", "volume_std20"] if col in data.columns]
    if not valid_cols:
        st.error("❌ 必要欄位不存在，無法繼續分析")
        return

    data = data.dropna(subset=valid_cols)

    if data.empty:
        st.error("❌ 有效資料筆數為 0，無法分析")
        return

    # 計算 z-score
    data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["anomaly"] = data["zscore_volume"].abs() > 2

    # 畫圖
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