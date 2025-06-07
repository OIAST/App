import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 技術分析選單，C 改為 XGBoost 分析
    analysis_option = st.selectbox(
        "選擇技術分析類型",
        ["統計量化分析", "A", "B", "XGBoost 漲跌預測"]
    )
    st.write(f"目前選擇：{analysis_option}")

    analysis_descriptions = {
        "統計量化分析": "成交量、20日均線及其標準差變動率分析，幫助判斷成交量波動與股價走勢。",
        "A": "選項 A 的分析說明，待補充。",
        "B": "選項 B 的分析說明，待補充。",
        "XGBoost 漲跌預測": "利用 XGBoost 模型結合技術指標預測未來股價漲跌，並展示特徵重要性。",
    }
    st.markdown(f"**分析說明：** {analysis_descriptions.get(analysis_option, '無說明')}")

    # 取得資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)
    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return
    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 計算技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["volume_std20_change"] = data["volume_std20"].pct_change()

    # 最近 30 筆資料的日期格式
    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%m/%d")

    if analysis_option == "統計量化分析":
        # 繪製三張圖
        col1, col2, col3 = st.columns(3)
        fig_size = (5, 3)

        with col1:
            st.write("📉 股價走勢 (Close)")
            fig_close, ax_close = plt.subplots(figsize=fig_size)
            ax_close.plot(dates, recent_data["Close"], color="green", label="Close Price")
            ax_close.set_title("Stock Closing Price")
            ax_close.set_xlabel("Date")
            ax_close.set_ylabel("Price")
            ax_close.tick_params(axis='x', labelsize=8)
            ax_close.grid(True)
            ax_close.legend()
            fig_close.autofmt_xdate(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_close)

        with col2:
            st.write("📈 成交量 & 20日均線")
            fig_vol, ax_vol = plt.subplots(figsize=fig_size)
            ax_vol.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
            ax_vol.plot(dates, recent_data["volume_ma20"], label="20-Day MA", color="orange")
            ax_vol.set_title("Volume and 20-Day MA")
            ax_vol.set_xlabel("Date")
            ax_vol.set_ylabel("Volume")
            ax_vol.tick_params(axis='x', labelsize=8)
            ax_vol.legend()
            ax_vol.grid(True)
            fig_vol.autofmt_xdate(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_vol)

        with col3:
            st.write("📉 20日標準差變動率")
            fig_std, ax_std = plt.subplots(figsize=fig_size)
            ax_std.plot(dates, recent_data["volume_std20_change"], color="purple", label="STD Change Rate")
            ax_std.axhline(0, color="gray", linestyle="--", linewidth=1)
            ax_std.set_title("20-Day STD Change Rate")
            ax_std.set_xlabel("Date")
            ax_std.set_ylabel("Change Rate")
            ax_std.tick_params(axis='x', labelsize=8)
            ax_std.legend()
            ax_std.grid(True)
            fig_std.autofmt_xdate(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_std)

    elif analysis_option == "XGBoost 漲跌預測":
        st.write("正在訓練 XGBoost 模型...")

        # 準備特徵與目標
        df = data.copy()
        df.dropna(inplace=True)

        # 目標：明天漲跌 (1 = 漲, 0 = 跌或持平)
        df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        df.dropna(inplace=True)

        features = ["Close", "Volume", "volume_ma20", "volume_std20", "volume_std20_change"]
        X = df[features]
        y = df["target"]

        # 分割資料集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        # 建立模型
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)

        # 預測與評估
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        st.write(f"模型準確度 (Accuracy): **{acc:.2%}**")

        # 顯示特徵重要性
        st.write("特徵重要性")
        fig_fi, ax_fi = plt.subplots()
        xgb.plot_importance(model, ax=ax_fi, max_num_features=10, importance_type='gain')
        plt.tight_layout()
        st.pyplot(fig_fi)

if __name__ == "__main__":
    st.title("股票技術分析工具")
    stock_input = st.text_input("輸入股票代碼（例如 AAPL）", value="AAPL")
    if stock_input:
        run(stock_input.upper())