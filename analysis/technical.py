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
    try:
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()
    except Exception as e:
        st.error(f"❌ 移動平均計算錯誤: {e}")
        return

    # 並排檢查欄位與 dropna（保證欄位存在才 drop）
    if "volume_ma20" not in data.columns or "volume_std20" not in data.columns:
        st.error("❌ 必要欄位缺失，無法繼續分析")
        return

    data = data.dropna().copy()  # 安全地刪除任何 NA 資料

    # 再確認資料夠用
    if data.empty:
        st.warning("⚠️ 有效資料不足，請選更長的區間")
        return

    # 計算 Z-score
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