# technical.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run(symbol, data):
    # 確認有 Volume 欄位
    if "Volume" not in data.columns:
        raise ValueError("⚠️ 請提供包含 Volume 欄位的 DataFrame")

    # 計算 20 天成交量移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 檢查是否成功計算出需要的欄位
    required_cols = ["volume_ma20", "volume_std20"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"⚠️ 無法計算移動平均，欄位遺失: {missing_cols}")

    # 先剔除計算 z-score 需要的欄位有 NaN 的列，避免錯誤
    data_clean = data.dropna(subset=required_cols + ["Volume"]).copy()

    # 計算 z-score volume
    data_clean["zscore_volume"] = (data_clean["Volume"] - data_clean["volume_ma20"]) / data_clean["volume_std20"]

    # 畫圖展示 Volume 和 z-score_volume
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,8), sharex=True)

    ax1.bar(data_clean.index, data_clean["Volume"], color="lightblue")
    ax1.set_title(f"{symbol} 成交量")
    ax1.set_ylabel("Volume")

    ax2.plot(data_clean.index, data_clean["zscore_volume"], color="red")
    ax2.axhline(0, color="black", linestyle="--")
    ax2.set_title(f"{symbol} 成交量 Z-Score")
    ax2.set_ylabel("Z-Score")

    plt.tight_layout()
    plt.show()

    return data_clean  # 回傳計算後資料方便後續使用