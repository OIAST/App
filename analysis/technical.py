# technical.py
import pandas as pd
import numpy as np
import streamlit as st  # 如果你是在 Streamlit 使用這個module才需要

def run(symbol, data=None):
    """
    參數說明：
    - symbol: 股票代碼（字串）
    - data: 預先抓好的 DataFrame，若 None 則嘗試自行抓取（範例中沒有內建抓資料功能）

    回傳值：
    - 加入了 volume_ma20、volume_std20、zscore_volume 的 DataFrame
    """

    # 假設外部已經提供 data，且欄位有 Volume
    if data is None:
        st.warning("⚠️ 請提供包含 Volume 欄位的 DataFrame")
        return None

    # 先確認必須欄位
    if "Volume" not in data.columns:
        st.warning("⚠️ 欄位 Volume 不存在，無法計算指標")
        return None

    # 計算20日移動平均與標準差
    data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
    data["volume_std20"] = data["Volume"].rolling(window=20).std()

    # 準備 dropna 的欄位列表，並確定這些欄位在 data 中存在
    subset_cols = ["volume_ma20", "volume_std20"]
    existing_cols = [col for col in subset_cols if col in data.columns]

    if len(existing_cols) < len(subset_cols):
        missing = list(set(subset_cols) - set(existing_cols))
        st.warning(f"⚠️ 欄位缺失無法計算：{missing}")
        return None

    # 去除在這些欄位中有缺失值的列，避免計算錯誤
    data = data.dropna(subset=existing_cols).copy()

    # 計算 z-score volume
    # 用 try-except 防止除以零或 NaN 引發錯誤
    try:
        data["zscore_volume"] = (data["Volume"] - data["volume_ma20"]) / data["volume_std20"]
    except Exception as e:
        st.warning(f"⚠️ 計算 z-score volume 時發生錯誤: {e}")
        return None

    # 回傳處理後的 DataFrame
    return data