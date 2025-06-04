import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------- 基本設定 ----------
sns.set(style="whitegrid")
plt.rcParams['axes.unicode_minus'] = False

st.title("📈 美股期權分析工具")

# ---------- 使用者輸入 ----------
symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()

if symbol:
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
                st.error(f"發生錯誤：{e}")
