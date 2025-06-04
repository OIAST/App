import streamlit as st
import yfinance as yf

def render_floating_price_box(symbol):
    ticker = yf.Ticker(symbol)
    try:
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return
        current = data['Close'][-1]
        previous = data['Close'][-2]
        change = current - previous
        pct = (change / previous) * 100
        color = 'green' if change >= 0 else 'red'
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(f"""
        <div id="price-box" class="draggable">
            <div style='font-size:14px; color:black;'>目前價格：</div>
            <div style='font-size:20px; font-weight:bold; color:{color};'>{current:.2f} {arrow}</div>
            <div style='font-size:14px; color:{color};'>漲跌：{change:+.2f} ({pct:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

    st.markdown("""
    <style>
    #price-box {
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: #ffffffcc;
        padding: 10px 15px;
        border: 1px solid #999;
        border-radius: 8px;
        z-index: 9999;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        cursor: move;
    }
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function () {
        const box = window.parent.document.querySelector('#price-box');
        if (box) {
            let isDragging = false;
            let offsetX, offsetY;
            box.addEventListener('mousedown', function (e) {
                isDragging = true;
                offsetX = e.clientX - box.getBoundingClientRect().left;
                offsetY = e.clientY - box.getBoundingClientRect().top;
            });
            window.parent.document.addEventListener('mousemove', function (e) {
                if (isDragging) {
                    box.style.left = (e.clientX - offsetX) + 'px';
                    box.style.top = (e.clientY - offsetY) + 'px';
                    box.style.bottom = 'auto';
                }
            });
            window.parent.document.addEventListener('mouseup', function () {
                isDragging = false;
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
