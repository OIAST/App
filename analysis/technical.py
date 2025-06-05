import yfinance as yf
import streamlit as st
import pandas as pd

def fetch_rsi(symbol: str, period: int = 14):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="3mo", interval="1d", auto_adjust=True)

    if "Close" not in data.columns or data.empty:
        return None, None

    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return data["Close"], rsi


def render_rsi_bar(symbol: str):
    adj_close, rsi = fetch_rsi(symbol)

    if adj_close is None or rsi is None or rsi.dropna().empty:
        st.warning("⚠️ 無法取得 RSI 資料。請確認股票代碼正確或稍後再試。")
        return

    current_price = adj_close.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    # RSI 區間設定
    rsi_min, rsi_max = 30, 70
    rsi_pos = (latest_rsi - rsi_min) / (rsi_max - rsi_min)
    rsi_pos = max(0, min(1, rsi_pos))  # 限制在 [0, 1] 範圍

    bar_width = 40  # 可調整條寬
    filled = int(bar_width * rsi_pos)
    empty = bar_width - filled

    rsi_bar = "⬛" * filled + "⬜" * empty

    st.subheader("📊 RSI 快速條")
    st.markdown(f"""
    <div style="font-family: monospace; font-size: 20px;">
        RSI: <b>{latest_rsi:.2f}</b><br>
        價格: ${current_price:.2f}<br>
        <span style="color:#888;">30</span> {rsi_bar} <span style="color:#888;">70</span>
    </div>
    """, unsafe_allow_html=True)


def run(symbol: str):
    st.header("📈 技術面分析")
    render_rsi_bar(symbol)