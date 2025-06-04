import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------- 基本設定 ----------
sns.set(style="whitegrid")
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="美股選擇權分析工具", layout="wide")
st.title("📈 美股分析工具")

# ---------- 使用者輸入 ----------
symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()
analysis_option = st.selectbox("選擇分析項目", ["基本面", "籌碼面", "技術面", "股價機率分析"])

# ---------- 顯示即時價格浮動視窗（左下角 + 可拖曳） ----------
if symbol:
    try:
        ticker = yf.Ticker(symbol)
        intraday = ticker.history(period="1d", interval="1m")
        if not intraday.empty:
            current_price = intraday['Close'][-1]
            st.markdown(
                f"""
                <style>
                #float-box {{
                    position: fixed;
                    bottom: 20px;
                    left: 20px;
                    width: 200px;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 10px;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                    cursor: move;
                    z-index: 9999;
                }}
                </style>

                <div id="float-box">
                    <strong>{symbol} 即時股價</strong><br>
                    <span style='font-size:18px; color:green;'>${current_price:.2f}</span>
                </div>

                <script>
                const box = document.getElementById('float-box');
                let isDragging = false, offsetX, offsetY;

                box.addEventListener('mousedown', function(e) {{
                    isDragging = true;
                    offsetX = e.clientX - box.getBoundingClientRect().left;
                    offsetY = e.clientY - box.getBoundingClientRect().top;
                }});

                document.addEventListener('mousemove', function(e) {{
                    if (isDragging) {{
                        box.style.left = (e.clientX - offsetX) + 'px';
                        box.style.top = (e.clientY - offsetY) + 'px';
                        box.style.bottom = 'auto';
                        box.style.right = 'auto';
                        box.style.position = 'fixed';
                    }}
                }});

                document.addEventListener('mouseup', function() {{
                    isDragging = false;
                }});
                </script>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"⚠️ 無法取得即時股價：{e}")

# ---------- 分析項目處理 ----------
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
                st.error(f"發生錯誤：{e}")
else:
    if analysis_option != "籌碼面":
        st.info(f"🔧 {analysis_option} 分析模組尚在開發中。")
