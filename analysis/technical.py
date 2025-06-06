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

    # 取得一年日線資料
    data = yf.download(symbol, period="1y", interval="1d", progress=False)

    # 確認資料是否有效
    if data.empty or "Volume" not in data.columns:
        st.error("⚠️ 無法取得資料或缺少 Volume 欄位。")
        return

    # 計算技術指標
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 建立一個 dataframe 儲存顯示用欄位，先篩掉前20筆無法計算的行
    display_data = data.dropna(subset=["volume_ma20", "volume_std20"]).copy()

    # 安全計算 zscore（避免出錯）
    display_data["zscore_volume"] = (
        (display_data["Volume"] - display_data["volume_ma20"]) / display_data["volume_std20"]
    ).round(2)

    # 格式化欄位加上「萬」
    display_data["Volume_fmt"] = display_data["Volume"].apply(format_volume)
    display_data["volume_ma20_fmt"] = display_data["volume_ma20"].apply(format_volume)
    display_data["volume_std20_fmt"] = display_data["volume_std20"].apply(format_volume)
    display_data["zscore_volume_fmt"] = display_data["zscore_volume"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )

    # 顯示結果（近30日）
    st.write("📈 Volume Z-score 分析（近 30 日）")
    st.dataframe(
        display_data[[
            "Volume_fmt", "volume_ma20_fmt", "volume_std20_fmt", "zscore_volume_fmt"
        ]].tail(30),
        use_container_width=True
    )