import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    # 確保 Volume 為數字
    if "Volume" not in data.columns:
        st.error("⚠️ 缺少 Volume 欄位")
        return

    # 強制轉成數字
    data["Volume"] = pd.to_numeric(data["Volume"])

    # 計算移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 診斷欄位問題
    required_cols = ["Volume", "volume_ma20", "volume_std20"]
    st.write("目前欄位：", data.columns.tolist())
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"❌ 缺少欄位：{missing_cols}")
        return

    # 計算 z-score（只針對有效值）
    try:
        valid = data.dropna(subset=required_cols)
        zscore = (valid["Volume"] - valid["volume_ma20"]) / valid["volume_std20"]
        data["zscore_volume"] = None
        data.loc[valid.index, "zscore_volume"] = zscore
    except Exception as e:
        st.error(f"Z-score 計算失敗：{e}")
        return

    # 顯示最近 30 筆資料（純數字）
    st.write("🔢 近 30 日成交量分析")
    recent = data.dropna(subset=["zscore_volume"]).tail(30)
    for date, row in recent.iterrows():
        st.write(
            f"📅 {date.date()}｜Volume: {row['Volume']:.0f}｜MA20: {row['volume_ma20']:.0f}｜STD20: {row['volume_std20']:.0f}｜Z-Score: {row['zscore_volume']:.2f}"
        )