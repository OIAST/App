import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 選擇大型股（例如 AAPL）
symbol = "AAPL"
data = yf.download(symbol, period="6mo", interval="1d")

# 計算 20 日移動平均與標準差（用於 Z-score）
data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
data["volume_std20"] = data["Volume"].rolling(window=20).std()
data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

# 偵測異常成交量（Z-score > 2）
data["anomaly"] = data["zscore_volume"].abs() > 2

# 繪圖：成交量與異常點
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(data.index, data["Volume"], color="skyblue", label="Volume")
ax1.scatter(
    data[data["anomaly"]].index,
    data[data["anomaly"]]["Volume"],
    color="red", label="Anomaly", zorder=5
)
ax1.set_title(f"{symbol} Volume Anomaly Detection (Z-score > 2)")
ax1.set_ylabel("Volume")
ax1.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()