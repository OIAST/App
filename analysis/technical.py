import yfinance as yf

def fetch_stock_data(symbol: str, period: str = "3mo", interval: str = "1d"):
    """
    從 Yahoo Finance 抓取指定股票的歷史資料
    :param symbol: 股票代碼（例如：TSLA）
    :param period: 資料區間，預設3個月
    :param interval: 資料間隔，預設為1天
    :return: 包含 OHLCV 的 DataFrame
    """
    data = yf.download(symbol, period=period, interval=interval)

    if data.empty:
        print(f"⚠️ 無法抓取 {symbol} 的資料。")
    elif "Volume" not in data.columns:
        print("⚠️ 無法取得成交量（Volume）欄位。")
    else:
        print(f"✅ 成功抓取 {symbol} 資料，共 {len(data)} 筆")
    
    return data

# 範例：抓取特斯拉股票資料
symbol = "TSLA"
data = fetch_stock_data(symbol)

# 顯示前幾筆資料
print(data.head())