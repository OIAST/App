import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from curl_cffi import requests

def get_options_data(symbol):
    url = f"https://query2.finance.yahoo.com/v7/finance/options/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, impersonate="chrome110")
        data = resp.json()
        return data
    except Exception as e:
        st.error(f"資料擷取失敗：{e}")
        return None

def run(symbol):
    raw = get_options_data(symbol)
    if not raw or 'optionChain' not in raw or not raw['optionChain']['result']:
        st.warning(f"⚠️ 找不到 {symbol} 的期權資料")
        return

    result = raw['optionChain']['result'][0]
    spot_price = result['quote']['regularMarketPrice']
    expirations = result['expirationDates']
    options_by_date = {e: f"{pd.to_datetime(e, unit='s').date()}" for e in expirations}
    
    expiry_timestamps = list(options_by_date.keys())
    expiry_labels = list(options_by_date.values())

    selected = st.selectbox("選擇期權到期日", expiry_labels)
    selected_ts = expiry_timestamps[expiry_labels.index(selected)]

    if st.button("更新圖表"):
        url = f"https://query2.finance.yahoo.com/v7/finance/options/{symbol}?date={selected_ts}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, headers=headers, impersonate="chrome110")
            chain = resp.json()
            opt_result = chain['optionChain']['result'][0]
            calls = pd.DataFrame(opt_result['options'][0]['calls'])
            puts = pd.DataFrame(opt_result['options'][0]['puts'])
            calls["type"] = "call"
            puts["type"] = "put"
            options_df = pd.concat([calls, puts])
            data = options_df[['strike', 'volume', 'impliedVolatility', 'type', 'lastPrice']].dropna()

            st.subheader("📊 成交量熱力圖")  
            pivot_vol = data.pivot_table(index='strike', columns='type', values='volume', aggfunc='sum', fill_value=0)  
            fig1, ax1 = plt.subplots(figsize=(10, 5))  
            sns.heatmap(pivot_vol, cmap="YlGnBu", cbar_kws={'label': 'Volume'}, ax=ax1)  
            ax1.set_title(f"{symbol} Options Volume Heatmap ({selected})")  
            st.pyplot(fig1)  

            st.subheader("📌 市場情緒圖")  
            fig2, ax2 = plt.subplots(figsize=(10, 5))  
            sns.scatterplot(data=data, x='volume', y='impliedVolatility', hue='type', alpha=0.7, s=100, ax=ax2)  
            ax2.set_title("Volume vs Implied Volatility")  
            st.pyplot(fig2)  

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

            st.subheader("📉 IV vs Strike（有成交量）")  
            filtered_data = data[data['volume'] > 0]  
            fig4, ax4 = plt.subplots(figsize=(10, 5))  
            sns.lineplot(data=filtered_data, x='strike', y='impliedVolatility', hue='type', marker='o', ax=ax4)  
            ax4.axvline(spot_price, color='red', linestyle='--', label=f"Spot = {spot_price:.2f}")  
            ax4.legend()  
            st.pyplot(fig4)  

        except Exception as e:
            st.error(f"錯誤：{e}")