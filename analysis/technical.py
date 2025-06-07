import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBClassifier, plot_importance
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 模型一：統計量化分析
def run_statistical(symbol):
    st.subheader(f"📊 統計量化分析：{symbol}")
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 資料錯誤或缺少 Volume 欄位")
        return

    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["volume_std20_change"] = data["volume_std20"].pct_change()

    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%m/%d")
    fig_size = (5, 3)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("📉 股價走勢")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["Close"], color="green")
        ax.set_title("Close")
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        st.write("📈 成交量 & MA20")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
        ax.plot(dates, recent_data["volume_ma20"], label="MA20", color="orange")
        ax.set_title("Volume & MA20")
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    with col3:
        st.write("📉 標準差變動率")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["volume_std20_change"], color="purple")
        ax.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax.set_title("STD Change Rate")
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True)
        st.pyplot(fig)

# 模型二：XGBoost 預測
def run_xgboost(symbol, model_source):
    st.subheader(f"🤖 XGBoost 模型預測分析：{symbol}（基於：{model_source}）")
    data = yf.download(symbol, period="180d", interval="1d", progress=False)

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 資料錯誤或缺少 Volume 欄位")
        return

    if model_source == "統計量化分析":
        data["Return"] = data["Close"].pct_change()
        data["Volume_MA20"] = data["Volume"].rolling(20).mean()
        data["Volume_STD20"] = data["Volume"].rolling(20).std()
        data["Label"] = (data["Return"].shift(-1) > 0).astype(int)
        data = data.dropna()

        features = ["Close", "Return", "Volume", "Volume_MA20", "Volume_STD20"]
        X = data[features]
        y = data["Label"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

        model = XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        st.write(f"✅ 模型準確度：**{accuracy:.2%}**")
        st.write("🔍 特徵使用：", features)

        # 顯示特徵重要性圖
        st.write("📊 特徵重要性")
        fig, ax = plt.subplots(figsize=(6, 4))
        plot_importance(model, ax=ax)
        st.pyplot(fig)

        st.markdown("""
        **模型說明：**
        - 使用你指定的技術分析模型當作特徵
        - 預測「明日收盤是否上漲」
        - 若準確度 > 50%，代表該技術模型具有預測潛力
        """)
    else:
        st.warning("⚠️ 目前僅支援『統計量化分析』作為基礎模型")

# 主控入口
def run(symbol):
    st.subheader(f"🔍 技術分析模型選擇：{symbol}")

    model_option = st.selectbox(
        "請選擇要執行的技術分析類型",
        ["統計量化分析", "技術指標 A", "技術指標 B", "XGBoost 準確度分析"]
    )

    if model_option == "統計量化分析":
        run_statistical(symbol)

    elif model_option == "技術指標 A":
        st.info("🚧 技術指標 A 功能尚未建置")

    elif model_option == "技術指標 B":
        st.info("🚧 技術指標 B 功能尚未建置")

    elif model_option == "XGBoost 準確度分析":
        st.markdown("✅ 請選擇欲分析的技術模型來源：")
        model_source = st.selectbox("選擇技術模型", ["統計量化分析"])  # 未來可新增更多模型
        if st.button("開始預測分析"):
            run_xgboost(symbol, model_source)