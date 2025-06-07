import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def run(symbol):
    st.subheader(f"📊 技術面分析：{symbol}")

    analysis_option = st.selectbox(
        "選擇技術分析類型",
        ["統計量化分析", "A", "B", "C"]
    )
    st.write(f"目前選擇：{analysis_option}")

    analysis_descriptions = {
        "統計量化分析": (
            "此分析包含成交量、20日均線及其標準差的變動率，幫助判斷成交量波動性及股價走勢，"
            "量能若與STD標準差同上代表市場熱度高，反之則代表大戶離場或市場減熱，"
            "另外ma均線提供長期量能，若量能低於均線，代表市場可能趨於保守。"
        ),
        "A": "選項 A 的分析說明，待補充。",
        "B": "選項 B 的分析說明，待補充。",
        "C": "選項 C 的分析說明，待補充。",
    }

    if analysis_option == "統計量化分析":
        st.markdown(f"**分析說明：** {analysis_descriptions['統計量化分析']}")

        data = yf.download(symbol, period="90d", interval="1d", progress=False)
        if data.empty:
            st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
            return

        # 計算20日均線及標準差
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()
        data["std_change_rate"] = data["volume_std20"].pct_change()  # 標準差變動率

        # 設定三張圖大小及格式
        fig_size = (6, 3)  # 可調整大小 (寬, 高)

        col1, col2, col3 = st.columns(3)

        # 成交量折線圖
        with col1:
            fig1, ax1 = plt.subplots(figsize=fig_size)
            ax1.plot(data.index, data["Volume"], label="成交量", color="blue")
            ax1.plot(data.index, data["volume_ma20"], label="20日均線", color="orange")
            ax1.set_title("成交量與20日均線")
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax1.get_xticklabels(), rotation=45, fontsize=8)
            ax1.legend()
            ax1.grid(True)
            st.pyplot(fig1)

        # 20日標準差折線圖
        with col2:
            fig2, ax2 = plt.subplots(figsize=fig_size)
            ax2.plot(data.index, data["volume_std20"], label="20日標準差", color="green")
            ax2.set_title("20日成交量標準差")
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax2.get_xticklabels(), rotation=45, fontsize=8)
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

        # 20日標準差變動率折線圖
        with col3:
            fig3, ax3 = plt.subplots(figsize=fig_size)
            ax3.plot(data.index, data["std_change_rate"], label="標準差變動率", color="red")
            ax3.set_title("標準差變動率")
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax3.get_xticklabels(), rotation=45, fontsize=8)
            ax3.legend()
            ax3.grid(True)
            st.pyplot(fig3)

    else:
        st.info("此分析類型尚未實作。")

# Streamlit主程式
if __name__ == "__main__":
    st.title("股票技術面分析")
    symbol = st.text_input("輸入股票代碼（例如：AAPL）", "AAPL")
    if symbol:
        run(symbol)