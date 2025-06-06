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

    # 計算技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # z-score：確保所有參與欄位都為 Series 且長度對齊
    zscore = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    data["zscore_volume"] = zscore

    # 格式化顯示
    display_df = data.copy()
    display_df["Volume_fmt"] = display_df["Volume"].apply(format_volume)
    display_df["volume_ma20_fmt"] = display_df["volume_ma20"].apply(format_volume)
    display_df["volume_std20_fmt"] = display_df["volume_std20"].apply(format_volume)
    display_df["zscore_volume_fmt"] = display_df["zscore_volume"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )

    # 顯示近 30 筆資料
    st.write("📈 Volume Z-score 分析（近 30 日）")
    st.dataframe(
        display_df[[
            "Volume_fmt", "volume_ma20_fmt", "volume_std20_fmt", "zscore_volume_fmt"
        ]].tail(30),
        use_container_width=True
    )