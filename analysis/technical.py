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

    # 技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 安全計算 z-score
    valid = data[["Volume", "volume_ma20", "volume_std20"]].dropna()
    zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
    data["zscore_volume"] = pd.Series(zscore, index=valid.index)

    # 格式化顯示
    display_df = data.copy()
    display_df["Volume_fmt"] = display_df["Volume"].apply(format_volume)
    display_df["volume_ma20_fmt"] = display_df["volume_ma20"].apply(format_volume)
    display_df["volume_std20_fmt"] = display_df["volume_std20"].apply(format_volume)
    display_df["zscore_volume_fmt"] = display_df["zscore_volume"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )

    st.write("📈 Volume Z-score 分析（近 30 日）")
    st.dataframe(
        display_df[[
            "Volume_fmt", "volume_ma20_fmt", "volume_std20_fmt", "zscore_volume_fmt"
        ]].tail(30),
        use_container_width=True
    )