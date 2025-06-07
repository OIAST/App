import yfinance as yf
import streamlit as st
import pandas as pd

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    # 抓取近 90 天日線資料
    data = yf.download(symbol, period="90d", interval="1d", progress=False)

    if data.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        return

    if "Volume" not in data.columns:
        st.error("⚠️ 資料中缺少 Volume 欄位。")
        return

    # 將 Volume 欄位強制轉換為數值型別，移除非數字資料
    data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")

    # 計算 20 日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 再次轉換為數字，確保沒有格式錯誤
    data["volume_ma20"] = pd.to_numeric(data["volume_ma20"], errors="coerce")
    data["volume_std20"] = pd.to_numeric(data["volume_std20"], errors="coerce")

    # 建立條件遮罩：三欄都為數字且 std ≠ 0
    mask = (
        data["Volume"].notna() &
        data["volume_ma20"].notna() &
        data["volume_std20"].notna() &
        (data["volume_std20"] != 0)
    )

    # 計算 Z-score 並寫入欄位
    data.loc[mask, "zscore_volume"] = (
        (data.loc[mask, "Volume"] - data.loc[mask, "volume_ma20"]) / data.loc[mask, "volume_std20"]
    )

    # 建立顯示用表格
    display_data = data[["Volume", "volume_ma20", "volume_std20", "zscore_volume"]].copy()
    display_data["zscore_volume"] = display_data["zscore_volume"].round(2)

    # 顯示最近 30 筆資料
    st.write("📈 成交量與 Z-score（近 30 日）")
    st.dataframe(display_data.tail(30))

# 範例執行（在 streamlit 主程式中會用 run("你的股票代碼") 呼叫）
# run("2330.TW")