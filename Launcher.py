import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from streamlit_option_menu import option_menu
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import financial_statement


# ====================================
#           技術分析代碼專區
# ====================================

#   模型一：PCA MODEL
def run_PCA_analysis(symbol):
        # 下載股票資料
        data = yf.download(symbol, period="180d", interval="1d", progress=False)

        # 計算技術指標
        data["RSI"] = data["Close"].pct_change().rolling(14).apply(
            lambda x: (x[x>0].sum()/abs(x).sum()*100) if abs(x).sum()>0 else 0)
        data["MA5"] = data["Close"].rolling(5).mean()
        data["MA10"] = data["Close"].rolling(10).mean()
        data["MA20"] = data["Close"].rolling(20).mean()
        data["MACD"] = data["Close"].ewm(span=12).mean() - data["Close"].ewm(span=26).mean()
        data["STD20"] = data["Close"].rolling(20).std()
        data["Volume"] = data["Volume"]

        # KD 指標
        low_min = data["Low"].rolling(9).min()
        high_max = data["High"].rolling(9).max()
        rsv = (data["Close"] - low_min) / (high_max - low_min) * 100
        data["K"] = rsv.ewm(com=2).mean()
        data["D"] = data["K"].ewm(com=2).mean()

        features = ["RSI","MA5","MA10","MA20","MACD","STD20","Volume","K","D"]
        df = data[features].dropna()

        # 標準化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df)

        # PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        # 圖一：PCA 投影圖
        fig1, ax1 = plt.subplots(figsize=(10,6))
        sc = ax1.scatter(X_pca[:,0], X_pca[:,1], c=range(len(X_pca)), cmap='viridis', alpha=0.6)
        ax1.set_xlabel("Principal Component 1")
        ax1.set_ylabel("Principal Component 2")
        ax1.set_title(f"PCA Projection of Technical Indicators for {symbol}")
        plt.colorbar(sc, label="Time Progression")
        ax1.grid(True)
        st.pyplot(fig1)

        # 圖二：Biplot
        fig2, ax2 = plt.subplots(figsize=(10,6))
        for i, feature in enumerate(features):
            ax2.arrow(0,0, pca.components_[0,i]*3, pca.components_[1,i]*3, color='red', alpha=0.5)
            ax2.text(pca.components_[0,i]*3.2, pca.components_[1,i]*3.2, feature,
                    color='black', fontsize=12, ha='center', va='center')
        ax2.scatter(X_pca[:,0], X_pca[:,1], alpha=0.3)
        ax2.axhline(0, color='gray', linestyle='--')
        ax2.axvline(0, color='gray', linestyle='--')
        ax2.set_xlabel("PC1")
        ax2.set_ylabel("PC2")
        ax2.set_title("Biplot of Technical Indicators")
        ax2.grid(True)
        st.pyplot(fig2)

#   模型二：XGBOOST MODEL
def run_xgboost_analysis(symbol):
    data = yf.download(symbol, period="720d", interval="1d", progress=False)

    # 均線計算
    data["ma20"] = data["Close"].rolling(window=20).mean()
    data["ma60"] = data["Close"].rolling(window=50).mean()

    # MACD計算
    ema12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema26 = data["Close"].ewm(span=26, adjust=False).mean()
    data["macd"] = ema12 - ema26
    data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()


    # 建立 target：未來 5 天的平均收盤價 > 今天收盤價 → 1，否則 0
    future_avg_5 = data["Close"].shift(-4).rolling(window=5).mean()
    data["target"] = (future_avg_5 > data["Close"]).astype(int)

    df = data[["Volume", "ma20", "ma60", "macd", "macd_signal", "target"]].copy()
    df.dropna(inplace=True)

    X = df[["Volume", "ma20", "ma60","macd","macd_signal"]]
    y = df["target"]


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # 模型訓練
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # 預測與評估
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    x_name = ["Volume", "Ma20", "Ma60","Macd-DIF","Macd-SHORT"]
    st.title(f"XGBoost Accuracy: {acc:.2%}")
    for name, imp in zip(x_name, model.feature_importances_):
        st.markdown(
        f"<p style='font-size:20px; font-weight:bold; color:#2E86C1;'>{name} : {imp:.2%}</p>",
        unsafe_allow_html=True)



# ====================================
#           籌碼分析代碼專區
# ====================================

#   模型一：Options Analysis Model
def run_options_analysis(symbol, expiry):
    ticker = yf.Ticker(symbol)
    spot_price = ticker.history(period="1d")['Close'][-1]
    options = ticker.option_chain(expiry)

    options_df = pd.concat([
        options.calls.assign(type='call'),
        options.puts.assign(type='put')
    ])
    data = options_df[['strike', 'volume', 'impliedVolatility', 'type', 'lastPrice']].dropna()

    # 📊 成交量熱力圖
    st.subheader("成交量熱力圖")
    pivot_vol = data.pivot_table(index='strike', columns='type', values='volume', aggfunc='sum', fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot_vol, cmap="YlGnBu", cbar_kws={'label': 'Volume'}, ax=ax)
    ax.set_title(f"{symbol} Options Volume Heatmap ({expiry})")
    st.pyplot(fig)

    # 📌 Volume vs IV
    st.subheader("Volume vs Implied Volatility")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=data, x='volume', y='impliedVolatility', hue='type', alpha=0.7, s=100, ax=ax)
    ax.grid(True)
    st.pyplot(fig)

    # 📈 IV 分布
    st.subheader("Implied Volatility Distribution")
    iv = data['impliedVolatility']
    mean_iv, std_iv = iv.mean(), iv.std()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(iv, bins=30, kde=True, color='purple', ax=ax)
    ax.axvline(mean_iv, color='red', linestyle='--', label=f"Mean={mean_iv:.3f}")
    ax.axvline(mean_iv + std_iv, color='green', linestyle='--', label=f"+1 Std={mean_iv+std_iv:.3f}")
    ax.axvline(mean_iv - std_iv, color='green', linestyle='--', label=f"-1 Std={mean_iv-std_iv:.3f}")
    ax.legend()
    st.pyplot(fig)

    # 📉 IV vs Strike
    st.subheader("IV vs Strike Price (Filtered by Volume)")
    filtered_data = data[data['volume'] > 0]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=filtered_data, x='strike', y='impliedVolatility', hue='type', marker='o', ax=ax)
    ax.axvline(spot_price, color='red', linestyle='--', label=f"Spot={spot_price:.2f}")
    ax.legend()
    st.pyplot(fig)

#   模型二：Isolation Forest Model
def run_isolation_forest(symbol, expiry, contamination=0.05, random_state=42):
    ticker = yf.Ticker(symbol)
    opt_chain = ticker.option_chain(expiry)
    calls = opt_chain.calls
    puts = opt_chain.puts

    calls = calls[(calls['volume'] > 0) & (calls['impliedVolatility'].notna())].copy()
    puts = puts[(puts['volume'] > 0) & (puts['impliedVolatility'].notna())].copy()
    calls['type'] = 'Call'
    puts['type'] = 'Put'
    df = pd.concat([calls, puts], ignore_index=True)

    features = df[['volume', 'impliedVolatility', 'strike']].copy()
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=random_state)
    model.fit(features)
    df['anomaly'] = model.predict(features)

    st.write(f"Random State: {random_state}")
    st.write(f"Total Contracts: {len(df)}")
    st.write(f"Anomalies Found: {(df['anomaly'] == -1).sum()}")

    # 📊 3D 異常偵測圖
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    colors, sizes, markers = [], [], []
    for _, row in df.iterrows():
        if row['anomaly'] == -1:
            sizes.append(80)
            colors.append('red' if row['type'] == 'Call' else 'purple')
            markers.append('*')
        else:
            sizes.append(20)
            colors.append('lightblue' if row['type'] == 'Call' else 'orange')
            markers.append('o')

    for marker in ['o', '*']:
        mask = [m == marker for m in markers]
        ax.scatter(
            df.loc[mask, 'volume'],
            df.loc[mask, 'impliedVolatility'],
            df.loc[mask, 'strike'],
            c=[colors[i] for i, m in enumerate(markers) if m == marker],
            s=[sizes[i] for i, m in enumerate(markers) if m == marker],
            marker=marker,
            alpha=0.8 if marker == '*' else 0.4,
            edgecolors='k'
        )

    ax.set_xlabel("Volume")
    ax.set_ylabel("Implied Volatility")
    ax.set_zlabel("Strike Price")
    ax.set_title(f"{symbol.upper()} Options Anomaly Detection ({expiry})")
    st.pyplot(fig)

    # 📋 結果表格
    st.dataframe(df[['contractSymbol', 'type', 'strike', 'volume', 'openInterest', 'impliedVolatility', 'anomaly']])



# ====================================
#           Streamlit 啟動器
# ====================================
st.set_page_config(layout="centered")

selected = option_menu(
    menu_title=None,
    options=["首頁", "基本分析", "技術分析", "籌碼分析", "相關資訊"],
    icons=["house", "caret-right", "caret-right", "caret-right", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

if selected == "首頁": 
    st.markdown(
    "<p style='font-size:18px; color:red;'>*部分功能於台灣時間下午13:00~晚上21:00暫停查詢服務</p>",
    unsafe_allow_html=True
    )
    st.image("https://www.ebc.com/upload/default/20230608/3a77502ab5dfce821f1c64982eccb091.jpg", caption="@ALL INFORMATION FROM YAHOO FINANCE")
    indices = {
        "道瓊工業指數": "^DJI",
        "那斯達克綜合指數": "^IXIC",
        "標普500指數": "^GSPC"
    }

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, (name, symbol) in enumerate(indices.items()):
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")

        if not data.empty:
            current_price = data['Close'][-1]
            previous_price = data['Close'][-2] if len(data) > 1 else current_price
            change = current_price - previous_price
            pct_change = (change / previous_price) * 100 if previous_price != 0 else 0
        else:
            current_price = change = pct_change = 0

        with cols[i]:
            st.metric(
                label=name,
                value=f"{current_price:.2f}",
                delta=f"{change:+.2f} ({pct_change:+.2f}%)",
                border=True
            )

elif selected == "基本分析":
    st.markdown(
    "<p style='font-size:16px; color:red;'>*尚在開發中，功能尚未完全</p>",
    unsafe_allow_html=True
    )
    symbol = st.text_input("輸入股票代碼 (如 AAPL)", value="")
    selection = st.selectbox("選擇項目",["財務報表","營收狀況"])
    if selection == "財務報表":
        financial_statement.launcher_1(symbol)
    elif selection == "營收狀況":
        financial_statement.launcher_2(symbol)

elif selected == "技術分析":
    symbol = st.text_input("輸入股票代碼 (如 AAPL)", value="")
    model_choice =st.selectbox("選擇模型", ["PCA Model", "XGBOOST Model"])
    if model_choice == "PCA Model" and symbol:
        if st.button("開始分析"):
            run_PCA_analysis(symbol)

    elif model_choice == "XGBOOST Model":
        st.markdown("<p style='font-size:16px; color:red;'>*此模型仍在開發階段，僅供實驗性質參考使用</p>",unsafe_allow_html=True)
        if st.button("開始分析"):
            run_xgboost_analysis(symbol)

elif selected == "籌碼分析":
    symbol = st.text_input("請輸入股票代碼（如 AAPL）", value="")
    if symbol:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        if expirations:
            expiry = st.selectbox("選擇到期日", expirations)
            model_choice =st.selectbox("選擇模型", ["Options Analysis Model", "Isolation Forest Model"])
            if model_choice == "Options Analysis Model":
                if st.button("開始分析"):
                    run_options_analysis(symbol.upper(), expiry)

            if model_choice == "Isolation Forest Model":
                contamination = st.select_slider("Contamination", options=[0.01, 0.05, 0.10, 0.20], value=0.05)
                random_choice = st.radio("Random State", ["Fixed 42", "Random"])
                rs = 42 if random_choice == "Fixed 42" else np.random.randint(0, 1000)
                if st.button("開始分析"):
                    run_isolation_forest(symbol.upper(), expiry, contamination=contamination, random_state=rs)
        else:
            st.warning(f"找不到 {symbol} 的期權資料")

elif selected == "相關資訊":
    st.markdown("<p style='font-size:28px; color:white;'>It's all invented by David Lin</p>",unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:grey;'>The infomation is from YAHOO FINANCE</p>",unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:grey;'>IDE BY JUPYTER, COLAB, VS CODE</p>",unsafe_allow_html=True)
    st.markdown(
    """
    <style>
    h1, h2, h3, p  {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 16px;
        color:red;
    }
    </style>
    """,
    unsafe_allow_html=True)
    st.markdown("基本分析  --  ※維修中")
    st.markdown("技術分析  --  PCA、XGBOOST(DEMO)")
    st.markdown("籌碼分析  --  OPTION ANALYSIS、ISOLATION FOREST")
    