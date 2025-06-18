import streamlit as st, pandas as pd, os
import finnhub, seaborn as sns, matplotlib.pyplot as plt

st.set_page_config(layout="wide")
f_client = finnhub.Client(api_key=os.getenv("FINNHUB_KEY"))

def run(symbol):
    res = f_client.option_chain(symbol)
    data = pd.DataFrame(res['data'])
    if data.empty:
        st.warning(f"⚠️ 找不到 {symbol} 的期權資料")
        return

    data['type'] = data['symbol'].apply(lambda s: 'call' if 'C' in s else 'put')
    spot = f_client.quote(symbol)['c']

    symbol_dates = data['expiry'].unique()
    expiry = st.selectbox("選擇期權到期日", sorted(symbol_dates))
    data = data[data['expiry']==expiry]

    data['iv_proxy'] = data['lastPrice'] / (abs(data['strike'] - spot) + 1e-3)

    # Heatmap 成交量
    pivot_vol = data.pivot_table(index='strike', columns='type', values='volume', aggfunc='sum', fill_value=0)
    fig1, ax1 = plt.subplots(figsize=(10,5))
    sns.heatmap(pivot_vol, cmap="YlGnBu", cbar_kws={'label':'Volume'}, ax=ax1)
    ax1.set_title(f"{symbol} Options Volume Heatmap ({expiry})")
    st.pyplot(fig1)

    # Volume vs IV proxy
    fig2, ax2 = plt.subplots(figsize=(10,5))
    sns.scatterplot(data=data, x='volume', y='iv_proxy', hue='type', alpha=0.7, s=100, ax=ax2)
    ax2.set_title("Volume vs IV Proxy")
    st.pyplot(fig2)

    # IV分布
    iv = data['iv_proxy']
    mean_iv, std_iv = iv.mean(), iv.std()
    fig3, ax3 = plt.subplots(figsize=(10,5))
    sns.histplot(iv, bins=30, kde=True, color='purple', ax=ax3)
    ax3.axvline(mean_iv, color='red', linestyle='--', label=f"Mean = {mean_iv:.3f}")
    ax3.axvline(mean_iv+std_iv, color='green', linestyle='--', label=f"+1 Std")
    ax3.axvline(mean_iv-std_iv, color='green', linestyle='--', label=f"-1 Std")
    ax3.legend()
    st.pyplot(fig3)

    # IV proxy vs strike (volume>0)
    filtered = data[data['volume'] > 0]
    fig4, ax4 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=filtered, x='strike', y='iv_proxy', hue='type', marker='o', ax=ax4)
    ax4.axvline(spot, color='red', linestyle='--', label=f"Spot = {spot:.2f}")
    ax4.legend()
    st.pyplot(fig4)