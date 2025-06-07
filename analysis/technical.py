import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

st.set_page_config(layout="wide")

st.title("成交量與股價技術分析")

# 參數設定
ticker = "AAPL"
period_days = 90

# 抓取資料
data = yf.download(ticker, period=f"{period_days}d", interval="1d")

# 計算成交量 20 日均線與標準差
data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
data["volume_std20"] = data["Volume"].rolling(window=20).std()

# 清理 NaN 用於繪圖
vol_ma_df = data[["Volume", "volume_ma20"]].dropna()
std_df = data["volume_std20"].dropna()

# 圖片大小
fig_size = (10, 4)

# 兩圖並排
col1, col2 = st.columns(2)

with col1:
    fig_vol_ma, ax_vol_ma = plt.subplots(figsize=fig_size)
    ax_vol_ma.plot(vol_ma_df.index, vol_ma_df["Volume"], label="Volume", color="blue")
    ax_vol_ma.plot(vol_ma_df.index, vol_ma_df["volume_ma20"], label="20-day MA", color="orange")
    ax_vol_ma.set_title("Volume & 20-day MA")
    ax_vol_ma.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax_vol_ma.get_xticklabels(), rotation=45, fontsize=8)
    ax_vol_ma.legend()
    ax_vol_ma.grid(True)
    st.pyplot(fig_vol_ma)

with col2:
    fig_std, ax_std = plt.subplots(figsize=fig_size)
    ax_std.plot(std_df.index, std_df, label="20-day Std Dev", color="green")
    ax_std.set_title("20-day Std Dev")
    ax_std.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax_std.get_xticklabels(), rotation=45, fontsize=8)
    ax_std.legend()
    ax_std.grid(True)
    st.pyplot(fig_std)

# 單獨股價折線圖
st.subheader("股價走勢圖")
fig_price, ax_price = plt.subplots(figsize=(20, 4))
ax_price.plot(data.index, data["Close"], label="Close Price", color="purple")
ax_price.set_title(f"{ticker} Close Price")
ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.setp(ax_price.get_xticklabels(), rotation=45, fontsize=8)
ax_price.legend()
ax_price.grid(True)
st.pyplot(fig_price)