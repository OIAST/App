import yfinance as yf
import pandas as pd
import streamlit as st

def format_volume(val):
    try:
        val = float(val)
        return f"{val/10000:.1f}萬" if val >= 10000 else f"{val:.0f}"
    except:
        return "-"

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取一年資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    # 檢查資料與 Volume 欄位
    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 資料錯誤或缺少 Volume 欄位。")
        return

    # 初始化欄位為 None，避免直接報錯
    data["volume_ma20"] = pd.NA
    data["volume_std20"] = pd.NA
    data["zscore_volume"] = pd.NA

    # 計算技術指標（有 NaN 沒關係）
    try:
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()
        zscore = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
        data["zscore_volume"] = zscore.round(2)
    except Exception as e:
        st.warning(f"⚠️ 無法計算技術指標：{e}")
        return

    # 格式化
    data["Volume_fmt"] = data["Volume"].apply(format_volume)
    data["volume_ma20_fmt"] = data["volume_ma20"].apply(format_volume)
    data["volume_std20_fmt"] = data["volume_std20"].apply(format_volume)
    data["zscore_volume_fmt"] = data["zscore_volume"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )

    # 顯示近 30 筆
    st.write("📈 Volume Z-score 分析（近 30 日）")
    display_cols = [
        "Volume_fmt", "volume_ma20_fmt", "volume_std20_fmt", "zscore_volume_fmt"
    ]
    st.dataframe(data[display_cols].tail(30), use_container_width=True)