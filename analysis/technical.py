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
        col1, col2, col3 = st.columns(3)

        # Price (Close) Chart
        with col1:
            fig1, ax1 = plt.subplots(figsize=fig_size)
            ax1.plot(data.index, data["Close"], label="Price", color="blue")
            ax1.set_title("Price")
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax1.get_xticklabels(), rotation=45, fontsize=8)
            ax1.legend()
            ax1.grid(True)
            st.pyplot(fig1)

        # Volume and 20-day MA Chart
        with col2:
            fig2, ax2 = plt.subplots(figsize=fig_size)
            ax2.plot(data.index, data["Volume"], label="Volume", color="blue")
            ax2.plot(data.index, data["volume_ma20"], label="20-day MA", color="orange")
            ax2.set_title("Volume & 20-day MA")
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax2.get_xticklabels(), rotation=45, fontsize=8)
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

        # 20-day Standard Deviation Chart
        with col3:
            fig3, ax3 = plt.subplots(figsize=fig_size)
            ax3.plot(data.index, data["volume_std20"], label="20-day Std Dev", color="green")
            ax3.set_title("20-day Std Dev")
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax3.get_xticklabels(), rotation=45, fontsize=8)
            ax3.legend()
            ax3.grid(True)
            st.pyplot(fig3)

    else:
        st.info("This analysis type is not yet implemented.")

if __name__ == "__main__":
    st.title("Stock Technical Analysis")
    symbol = st.text_input("Enter stock symbol (e.g., AAPL)", "AAPL")
    if symbol:
        run(symbol)