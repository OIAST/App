import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
##from sklearn.model_selection import train_test_split
##from sklearn.metrics import accuracy_score
##from xgboost import XGBClassifier
import numpy as np

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    analysis_option = st.selectbox(
        "選擇技術分析類型",
        ["統計量化分析", "XGBoost 分析"]
    )
    st.write(f"目前選擇：{analysis_option}")

    if analysis_option == "統計量化分析":
        run_statistical(symbol)

    elif analysis_option == "XGBoost 分析":
        model_option = st.selectbox(
            "選擇技術模型來源",
            ["統計量化模型"]
        )
        if model_option == "統計量化模型":
            run_xgboost_from_statistical(symbol)

def run_statistical(symbol):
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或資料格式錯誤。")
        return

    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["volume_std20_change"] = data["volume_std20"].pct_change()

    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%m/%d")
    fig_size = (5, 3)

    # 第一排圖
    col1, col2 = st.columns(2)

    with col1:
        st.write("📈 成交量 & 20日均線")
        fig1, ax1 = plt.subplots(figsize=fig_size)
        ax1.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
        ax1.plot(dates, recent_data["volume_ma20"], label="20-Day MA", color="orange")
        ax1.set_title("Volume and 20-Day MA", fontsize=10)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Volume")
        ax1.tick_params(axis='x', labelsize=7)
        ax1.tick_params(axis='y', labelsize=8)
        ax1.grid(True)
        ax1.legend(fontsize=8)
        fig1.autofmt_xdate(rotation=45)
        st.pyplot(fig1)

    with col2:
        st.write("📉 20日標準差變動率")
        fig2, ax2 = plt.subplots(figsize=fig_size)
        ax2.plot(dates, recent_data["volume_std20_change"], color="purple", label="STD Change Rate")
        ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax2.set_title("20-Day STD Change Rate", fontsize=10)
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Change Rate")
        ax2.tick_params(axis='x', labelsize=7)
        ax2.tick_params(axis='y', labelsize=8)
        ax2.grid(True)
        ax2.legend(fontsize=8)
        fig2.autofmt_xdate(rotation=45)
        st.pyplot(fig2)

    # 第二排圖：收盤價
    st.write("📊 收盤價走勢 (Close Price)")
    fig3, ax3 = plt.subplots(figsize=(10, 3.5))
    ax3.plot(dates, recent_data["Close"], color="green", label="Close Price")
    ax3.set_title("Closing Price Trend", fontsize=10)
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Price")
    ax3.tick_params(axis='x', labelsize=8)
    ax3.tick_params(axis='y', labelsize=8)
    ax3.grid(True)
    ax3.legend(fontsize=8)
    fig3.autofmt_xdate(rotation=45)
    st.pyplot(fig3)

def run_xgboost_from_statistical(symbol):
    data = yf.download(symbol, period="180d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或資料格式錯誤。")
        return

    # 建立特徵
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["volume_std20_change"] = data["volume_std20"].pct_change()
    data["close_ma5"] = data["Close"].rolling(window=5).mean()
    data["close_ma20"] = data["Close"].rolling(window=20).mean()

    # 建立標籤：若未來5日平均價格 > 今日，則為1，否則為0
    data["future_avg_5"] = data["Close"].shift(-5).rolling(window=5).mean()
    data["target"] = (data["future_avg_5"] > data["Close"]).astype(int)

    # 特徵欄位
    features = ["volume_ma20", "volume_std20", "volume_std20_change", "close_ma5", "close_ma20"]
    data = data.dropna(subset=features + ["target"])

    X = data[features]
    y = data["target"]

    # 拆分資料
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # 訓練模型
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # 預測與準確率
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    st.success(f"模型預測準確率：{acc:.2%}")

    # 特徵重要性
    st.write("📌 特徵重要性")
    importance = model.feature_importances_
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance (%)": (importance / importance.sum() * 100).round(2)
    }).sort_values("Importance (%)", ascending=False)

    st.dataframe(importance_df.reset_index(drop=True))

# Streamlit 主程式
if __name__ == "__main__":
    st.title("股票技術分析工具")
    stock_input = st.text_input("輸入股票代碼（例如 AAPL）", value="AAPL")
    if stock_input:
        run(stock_input.upper())