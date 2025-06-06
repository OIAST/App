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

    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 資料錯誤或缺少 Volume 欄位。")
        return

    # 技術指標計算（不移除 NaN，直接處理）
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()
    data["zscore_volume"] = (
        (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    ).round(2)

    # 安全格式化（即使 NaN 也能處理）
    data["Volume_fmt"] = data["Volume"].apply(format_volume)
    data["volume_ma20_fmt"] = data["volume_ma20"].apply(format_volume)
    data["volume_std20_fmt"] = data["volume_std20"].apply(format_volume)
    data["zscore_volume_fmt"] = data["zscore_volume"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )

    # 顯示近30筆，包含 NaN 也沒關係
    st.write("📈 Volume Z-score 分析（近 30 日）")
    st.dataframe(
        data[[
            "Volume_fmt", "volume_ma20_fmt", "volume_std20_fmt", "zscore_volume_fmt"
        ]].tail(30),
        use_container_width=True
    )