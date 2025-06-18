import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from finnhub import Client
import os

print(type(os.environ))

# 初始化 API client
finnhub_client = Client(api_key=os.environ.get("FINNHUB_API_KEY"))


def run(symbol):
    try:
        # 取得整份期權資料
        res = finnhub_client.option_chain(symbol=symbol)
        raw_data = res.get("data", [])

        if not raw_data:
            st.warning(f"⚠️ 找不到 {symbol} 的期權資料")
            return

        df = pd.DataFrame(raw_data)

        # 找出所有可選到期日
        expirations = sorted(df['expiry'].dropna().unique())
        expiry = st.selectbox("選擇期權到期日", expirations)

        # 篩選出選定到期日的資料
        filtered = df[df['expiry'] == expiry].copy()

        if filtered.empty:
            st.warning("該到期日無期權資料")
            return

        spot_price = res.get("quote", {}).get("c")  # 嘗試抓現價 (若無回傳則跳過)
        
        # 處理資料欄位一致性
        filtered = filtered.rename(columns={
            'strikePrice': 'strike',
            'volume': 'volume',
            'impliedVolatility': 'impliedVolatility',
            'type': 'type',
            'lastPrice': 'lastPrice'
        })

        filtered = filtered[['strike', 'volume', 'impliedVolatility', 'type', 'lastPrice']].dropna()

        st.subheader("📊 成交量熱力圖")
        pivot_vol = filtered.pivot_table(index='strike', columns='type', values='volume', aggfunc='sum', fill_value=0)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_vol, cmap="YlGnBu", cbar_kws={'label': 'Volume'}, ax=ax1)
        ax1.set_title(f"{symbol} Options Volume Heatmap ({expiry})")
        st.pyplot(fig1)

        st.subheader("📌 市場情緒圖")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=filtered, x='volume', y='impliedVolatility', hue='type', alpha=0.7, s=100, ax=ax2)
        ax2.set_title("Volume vs Implied Volatility")
        st.pyplot(fig2)

        st.subheader("📈 IV 分布圖")
        iv = filtered['impliedVolatility']
        mean_iv = iv.mean()
        std_iv = iv.std()
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.histplot(iv, bins=30, kde=True, color='purple', ax=ax3)
        ax3.axvline(mean_iv, color='red', linestyle='--', label=f"Mean = {mean_iv:.3f}")
        ax3.axvline(mean_iv + std_iv, color='green', linestyle='--', label=f"+1 Std = {mean_iv + std_iv:.3f}")
        ax3.axvline(mean_iv - std_iv, color='green', linestyle='--', label=f"-1 Std = {mean_iv - std_iv:.3f}")
        ax3.legend()
        st.pyplot(fig3)

        st.subheader("📉 IV vs Strike（有成交量）")
        filtered_data = filtered[filtered['volume'] > 0]
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=filtered_data, x='strike', y='impliedVolatility', hue='type', marker='o', ax=ax4)
        if spot_price:
            ax4.axvline(spot_price, color='red', linestyle='--', label=f"Spot = {spot_price:.2f}")
            ax4.legend()
        st.pyplot(fig4)

    except Exception as e:
        st.error(f"錯誤：{e}")
        
        
print("res type:", type(res))
print("res content:", res)