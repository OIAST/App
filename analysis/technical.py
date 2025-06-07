import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from xgboost import XGBClassifier, plot_importance
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -------------------------------------
# 主功能
# -------------------------------------
def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 技術分析選單
    analysis_option = st.selectbox(
        "選擇技術分析類型",
        ["統計量化分析", "A", "B", "XGBoost 預測分析"]
    )
    st.write(f"目前選擇：{analysis_option}")

    # 說明文字
    analysis_descriptions = {
        "統計量化分析": "此分析包含成交量、20日均線及其標準差的變動率，幫助判斷成交量波動性及股價走勢。",
        "A": "選項 A 的分析說明，待補充。",
        "B": "選項 B 的分析說明，待補充。",
        "XGBoost 預測分析": "使用技術指標訓練 XGBoost 模型，預測隔日股價是否上漲。",
    }
    st.markdown(f"**分析說明：** {analysis_descriptions.get(analysis_option, '無說明')}")

    # 抓取近 90 天資料
    df = yf.download(symbol, period="90d", interval="1d", progress=False)

    if df.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return
    if "Volume" not in df.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 統計量化指標
    df["volume_ma20"] = df["Volume"].rolling(window=20).mean()
    df["volume_std20"] = df["Volume"].rolling(window=20).std()
    df["volume_std20_change"] = df["volume_std20"].pct_change()

    # 加入其他技術指標
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    exp1 = df["Close"].ewm(span=12).mean()
    exp2 = df["Close"].ewm(span=26).mean()
    df["MACD"] = exp1 - exp2
    df["zscore_volume"] = (df["Volume"] - df["volume_ma20"]) / df["volume_std20"]

    # -----------------------------
    # 模組選擇
    # -----------------------------
    if analysis_option == "統計量化分析":
        plot_quantitative(df)
    elif analysis_option == "XGBoost 預測分析":
        xgboost_model(df)
    else:
        st.info("此選項尚未實作，敬請期待。")

# -------------------------------------
# 畫統計量化圖表
# -------------------------------------
def plot_quantitative(data):
    recent_data = data.tail(30)
    dates = recent_data.index.strftime("%m/%d")
    col1, col2, col3 = st.columns(3)
    fig_size = (5, 3)

    with col1:
        st.write("📉 股價走勢 (Close)")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["Close"], color="green")
        ax.set_title("Stock Closing Price")
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        st.write("📈 成交量 & 20日均線")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["Volume"], label="Volume", color="skyblue")
        ax.plot(dates, recent_data["volume_ma20"], label="MA20", color="orange")
        ax.set_title("Volume and 20-Day MA")
        ax.tick_params(axis='x', labelsize=8)
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    with col3:
        st.write("📉 20日標準差變動率")
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(dates, recent_data["volume_std20_change"], color="purple")
        ax.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax.set_title("20-Day STD Change Rate")
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True)
        st.pyplot(fig)

# -------------------------------------
# XGBoost 預測模型
# -------------------------------------
def xgboost_model(df: pd.DataFrame):
    st.subheader("📘 XGBoost 模型預測漲跌")

    features = ['RSI', 'MACD', 'zscore_volume', 'SMA20', 'EMA20']
    if any(f not in df.columns for f in features):
        st.warning("缺少必要的技術指標欄位，請確認資料。")
        return

    df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    df.dropna(subset=features + ["target"], inplace=True)

    X = df[features]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    st.success(f"模型預測準確率：{acc:.2%}")

    st.markdown("📌 技術指標影響力")
    fig, ax = plt.subplots()
    plot_importance(model, ax=ax, importance_type='gain', show_values=False)
    st.pyplot(fig)

    st.markdown("📋 預測結果預覽")
    df_pred = df.iloc[-len(y_test):].copy()
    df_pred["預測"] = y_pred
    st.dataframe(df_pred[["Close", "target", "預測"]].tail(10))