import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

import bcrypt

st.set_page_config(layout="wide")
st.title("🔐 請先登入")

# 預設使用者資料
username_correct = "david"
hashed_password = b"$2b$12$Ev/07R9qZweCzLoTo5diUO3L1R8ydI7Vp.Cv2MQs7zY8Mw09/dMyy"  # bytes格式

# 建立 session state 追蹤登入狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        if username == username_correct and bcrypt.checkpw(password.encode(), hashed_password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"登入成功，歡迎 {username}！")
        else:
            st.error("帳號或密碼錯誤")

def logout():
    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

if not st.session_state.logged_in:
    login()
else:
    st.write(f"👋 歡迎 {st.session_state.username}！")
    logout()


    # 以下才是你原本的網站主程式 ↓↓↓↓↓

# ---------- 基本設定 ----------
sns.set(style="whitegrid")
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(layout="wide")

st.title("📈 美股分析工具")

# ---------- 輸入與選擇 ----------
symbol = st.text_input("輸入股票代碼（例如：TSLA）", value="TSLA").upper()
analysis_type = st.selectbox("選擇分析項目", ["基本面", "籌碼面", "技術面", "股價機率分析"])

# ---------- 股價浮動視窗 ----------
def render_floating_price_box(symbol):
    ticker = yf.Ticker(symbol)
    try:
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return
        current = data['Close'][-1]
        previous = data['Close'][-2]
        change = current - previous
        pct = (change / previous) * 100
        color = 'green' if change >= 0 else 'red'
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(
            f"""
            <div id="price-box" class="draggable">
                <div style='font-size:14px; color:black;'>目前價格：</div>
                <div style='font-size:20px; font-weight:bold; color:{color};'>{current:.2f} {arrow}</div>
                <div style='font-size:14px; color:{color};'>漲跌：{change:+.2f} ({pct:+.2f}%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

# 定時刷新
st_autorefresh = st.experimental_rerun if datetime.datetime.now().second % 180 == 0 else lambda: None
render_floating_price_box(symbol)

# ---------- 籌碼面分析 ----------
if analysis_type == "籌碼面" and symbol:
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

                # 圖表 3：IV 分布圖
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

                # 圖表 4：IV vs Strike（有成交量）
                st.subheader("📉 IV vs Strike（有成交量）")
                filtered_data = data[data['volume'] > 0]
                fig4, ax4 = plt.subplots(figsize=(10, 5))
                sns.lineplot(data=filtered_data, x='strike', y='impliedVolatility', hue='type', marker='o', ax=ax4)
                ax4.axvline(spot_price, color='red', linestyle='--', label=f"Spot = {spot_price:.2f}")
                ax4.legend()
                st.pyplot(fig4)

            except Exception as e:
                st.error(f"錯誤：{e}")

# ---------- 空值分析項目 ----------
elif analysis_type in ["基本面", "技術面", "股價機率分析"]:
    st.info(f"🔧 『{analysis_type}』尚未實作，請選擇『籌碼面』進行期權分析。")

# ---------- 可拖曳浮動視窗的 CSS + JS ----------
st.markdown("""
<style>
#price-box {
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: #ffffffcc;
    padding: 10px 15px;
    border: 1px solid #999;
    border-radius: 8px;
    z-index: 9999;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    cursor: move;
}
</style>
<script>
document.addEventListener('DOMContentLoaded', function () {
    const box = window.parent.document.querySelector('#price-box');
    if (box) {
        let isDragging = false;
        let offsetX, offsetY;

        box.addEventListener('mousedown', function (e) {
            isDragging = true;
            offsetX = e.clientX - box.getBoundingClientRect().left;
            offsetY = e.clientY - box.getBoundingClientRect().top;
        });

        window.parent.document.addEventListener('mousemove', function (e) {
            if (isDragging) {
                box.style.left = (e.clientX - offsetX) + 'px';
                box.style.top = (e.clientY - offsetY) + 'px';
                box.style.bottom = 'auto';  // Reset bottom positioning
            }
        });

        window.parent.document.addEventListener('mouseup', function () {
            isDragging = false;
        });
    }
});
</script>
""", unsafe_allow_html=True)
