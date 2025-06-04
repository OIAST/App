import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ---------- 基本設定 ----------
sns.set(style="whitegrid")
plt.rcParams['axes.unicode_minus'] = False

# ---------- 自動刷新（每 3 分鐘） ----------
st_autorefresh(interval=180000, key="自動刷新")  # 每 3 分鐘（180000ms）自動刷新一次

st.title("📊 美股選擇權分析工具")

# ---------- 使用者輸入 ----------
symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()
analysis_option = st.selectbox("選擇分析項目", ["基本面", "籌碼面", "技術面", "股價機率分析"])

# ---------- 顯示目前即時股價 ----------
if symbol:
    try:
        ticker = yf.Ticker(symbol)
        intraday = ticker.history(period="1d", interval="1m")
        if not intraday.empty:
            current_price = intraday['Close'][-1]
            st.markdown(
                f"""
                <div style='position:fixed; bottom:10px; right:10px; background-color:#f9f9f9;
                            padding:12px; border-radius:10px; box-shadow: 0 0 10px rgba(0,0,0,0.3);
                            font-size:14px;'>
                    <b>{symbol} 即時股價：</b><br>
                    <span style='font-size:18px; color:#007700;'>${current_price:.2f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"⚠️ 無法取得即時股價：{e}")

# ---------- 籌碼面分析 ----------
if symbol and analysis_option == "籌碼面":
    ticker = yf.Ticker(symbol)
    expirations = ticker.options

    if not expirations:
        st.warning(f"⚠️ 找不到 {symbol} 的期權資料")
    else:
        expiry = st.selectbox("選擇期權到期日", expirations)
        if st.button("更新圖表"):
            try:
                spot_price = ticker.history(period="1d")['Close'][-1]
                options = ticker.option_chain(expiry)
                options_df = pd.concat([
                    options.calls.assign(type='call'),
                    options.puts.assign(type='put')
                ])
                data = options_df[['strike', 'volume', 'impliedVolatility', 'type', 'lastPrice']].dropna()

                # 圖表 1：成交量熱力圖
                st.subheader("📊 成交量熱力圖")
                pivot_vol = data.pivot_table(index='strike', columns='type', values='volume', aggfunc='sum', fill_value=0)
                pivot_vol = pivot_vol.astype(int)
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                sns.heatmap(pivot_vol, cmap="YlGnBu", cbar_kws={'label': 'Volume'}, ax=ax1)
                ax1.set_title(f"{symbol} Options Volume Heatmap ({expiry})")
                st.pyplot(fig1)

                # 圖表 2：市場情緒圖
                st.subheader("📌 市場情緒圖")
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                sns.scatterplot(data=data, x='volume', y='impliedVolatility', hue='type', alpha=0.7, s=100, ax=ax2)
                ax2.set_title("Volume vs Implied Volatility")
                st.pyplot(fig2)

                # 圖表 3：IV 分布
                st.subheader("📈 IV 分布圖")
                iv = data['impliedVolatility']
                mean_iv = iv.mean()
                std_iv = iv.std()
                fig3, ax3 = plt.subplots(figsize=(10, 5))
                sns.histplot(iv, bins=30, kde=True, color='purple', ax=ax3)
                ax3.axvline(mean_iv, color='red', linestyle='--', label=f"Mean = {mean_iv:.3f}")
                ax3.axvline(mean_iv + std_iv, color='green', linestyle='--', label=f"+1 Std = {mean_iv + std_iv:.3f}")
                ax3.axvline(mean_iv - std_iv, color='green', linestyle='--', label=f"-1 Std = {mean_iv - std_iv:.3f}")
                ax3.legend()
                st.pyplot(fig3)

                # 圖表 4：IV vs Strike
                st.subheader("📉 IV vs Strike（有成交量）")
                filtered_data = data[data['volume'] > 0]
                fig4, ax4 = plt.subplots(figsize=(10, 5))
                sns.lineplot(data=filtered_data, x='strike', y='impliedVolatility', hue='type', marker='o', ax=ax4)
                ax4.axvline(spot_price, color='red', linestyle='--', label=f"Spot Price = {spot_price:.2f}")
                ax4.legend()
                st.pyplot(fig4)

            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")

# ---------- 其他分析項目為空值佔位 ----------
elif analysis_option in ["基本面", "技術面", "股價機率分析"]:
    st.info("📌 此分析項目尚未實作，敬請期待。")
