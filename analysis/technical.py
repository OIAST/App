import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def run(symbol):
    st.subheader(f"📊 Technical Analysis: {symbol}")

    analysis_option = st.selectbox(
        "Select Technical Analysis Type",
        ["Quantitative Analysis", "A", "B", "C"]
    )
    st.write(f"Current Selection: {analysis_option}")

    analysis_descriptions = {
        "Quantitative Analysis": (
            "This analysis includes volume, 20-day moving average (MA), "
            "and the rate of change of the 20-day standard deviation (STD) to help judge volume volatility and price trends. "
            "If volume and STD increase together, it indicates high market activity; otherwise, it may indicate major investors exiting or market cooling down. "
            "Additionally, the MA provides a long-term volume trend; if volume is below the MA, the market might be conservative."
        ),
        "A": "Description for option A (to be added).",
        "B": "Description for option B (to be added).",
        "C": "Description for option C (to be added).",
    }

    if analysis_option == "Quantitative Analysis":
        st.markdown(f"**Analysis Description:** {analysis_descriptions['Quantitative Analysis']}")

        data = yf.download(symbol, period="20d", interval="1d", progress=False)
        if data.empty:
            st.error("⚠️ Unable to fetch data. Please check the stock symbol.")
            return

        # Calculate 20-day moving average and std deviation for volume
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        data["volume_std20"] = data["Volume"].rolling(window=20).std()

        fig_size = (6, 3)

        # 第一列：Volume & 20-day MA 與 20-day Std Dev 並排
        col1, col2 = st.columns(2)

        with col1:
            fig_vol_ma, ax_vol_ma = plt.subplots(figsize=fig_size)
            ax_vol_ma.plot(data.index, data["Volume"], label="Volume", color="blue")
            ax_vol_ma.plot(data.index, data["volume_ma20"], label="20-day MA", color="orange")
            ax_vol_ma.set_title("Volume & 20-day MA")
            ax_vol_ma.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax_vol_ma.get_xticklabels(), rotation=45, fontsize=8)
            ax_vol_ma.legend()
            ax_vol_ma.grid(True)
            st.pyplot(fig_vol_ma)

        with col2:
            fig_std, ax_std = plt.subplots(figsize=fig_size)
            ax_std.plot(data.index, data["volume_std20"], label="20-day Std Dev", color="green")
            ax_std.set_title("20-day Std Dev")
            ax_std.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax_std.get_xticklabels(), rotation=45, fontsize=8)
            ax_std.legend()
            ax_std.grid(True)
            st.pyplot(fig_std)

        # 第二列：價格圖獨立顯示
        st.markdown("### Price Chart")
        fig_price, ax_price = plt.subplots(figsize=(12, 3))
        ax_price.plot(data.index, data["Close"], label="Price", color="blue")
        ax_price.set_title("Price")
        ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.setp(ax_price.get_xticklabels(), rotation=45, fontsize=8)
        ax_price.legend()
        ax_price.grid(True)
        st.pyplot(fig_price)

    else:
        st.info("This analysis type is not yet implemented.")

if __name__ == "__main__":
    st.title("Stock Technical Analysis")
    symbol = st.text_input("Enter stock symbol (e.g., AAPL)", "AAPL")
    if symbol:
        run(symbol)