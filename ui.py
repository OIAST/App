import streamlit as st
import requests

API_KEY = '你的API金鑰'  # 建議放 secrets.toml

def render_floating_price_box(symbol):
    try:
        # 取得現價資料
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}'
        resp = requests.get(url).json()

        current = resp['c']
        previous = resp['pc']

        if not current or not previous:
            return

        change = current - previous
        pct = (change / previous) * 100
        color = 'green' if change >= 0 else 'red'
        arrow = "▲" if change >= 0 else "▼"

        st.markdown(f"""
        <div id="price-box" class="draggable">
            <div style='font-size:14px; color:black;'>目前價格（{symbol.upper()}）：</div>
            <div style='font-size:20px; font-weight:bold; color:{color};'>{current:.2f} {arrow}</div>
            <div style='font-size:14px; color:{color};'>漲跌：{change:+.2f} ({pct:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"資料取得失敗：{e}")

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