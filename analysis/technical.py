import yfinance as yf
import pandas as pd

# 抓取資料
symbol = "2330.TW"
data = yf.download(symbol, period="90d", interval="1d", progress=False)

# 處理 Volume 資料
data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")

# 計算 20 日移動平均與標準差
data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
data["volume_std20"] = data["Volume"].rolling(window=20).std()

# 計算 z-score
data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]

# 印出格式與內容
print("📌 資料型態 dtype：")
print("Volume:", data["Volume"].dtype)
print("volume_ma20:", data["volume_ma20"].dtype)
print("volume_std20:", data["volume_std20"].dtype)
print("zscore_volume:", data["zscore_volume"].dtype)

print("\n📌 前 10 筆數據預覽：")
print(data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].head(10))