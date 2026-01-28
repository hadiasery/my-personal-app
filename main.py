import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 15 ثانية
st_autorefresh(interval=15000, key="v42_1_pro_final")

st.set_page_config(page_title="رادار القناص V42.1", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق CSS الاحترافي (مخطط، خط كبير، نص أسود) ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 98%; }
    .stApp { background-color: white; }
    
    .full-width-table { 
        width: 100% !important; 
        border-collapse: collapse; 
        background-color: white;
        border: 2px solid black !important;
    }
    
    th { 
        background-color: #1e293b !important; 
        color: white !important; 
        text-align: center !important; 
        padding: 12px; 
        font-size: 18px;
        border: 2px solid black !important;
    }
    
    td { 
        text-align: center !important; 
        font-weight: 900 !important; 
        border: 2px solid black !important; 
        padding: 10px 5px !important; 
        font-size: 20px !important; 
        color: black !important; 
    }
    
    /* الألوان الأساسية */
    .row-calm { background-color: #ffffff !important; }
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }   
    .iv-blue { background-color: #7dd3fc !important; } 
    
    .legend-box { width: 250px; padding: 12px; border: 2px solid black; border-radius: 8px; background-color: #f8fafc; }
    .leg-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; font-weight: bold; color: black; }
    .leg-color { width: 20px; height: 20px; margin-right: 10px; border-radius: 3px; border: 1px solid black; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

results = []
sound_triggered = False

try:
    # جلب بيانات كافية لحساب EMA 200 (نحتاج 5 أيام بفاصل دقيقة)
    data = yf.download(STOCKS, period='5d', interval='1m', group_by='ticker', progress=False)
    
    for sym in STOCKS:
        df = data[sym].dropna()
        if not df.empty and len(df) > 200:
            curr_p = float(df['Close'].iloc[-1])
            # حساب التغير اليومي (مقارنة بإغلاق أمس)
            prev_close = yf.Ticker(sym).info.get('previousClose', curr_p)
            change_pct = ((curr_p - prev_close) / prev_close) * 100
            
            # حساب المؤشرات
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            rsi_val = ta.rsi(df['Close'], length=14).iloc[-1]
            ema200 = ta.ema(df['Close'], length=200).iloc[-1]
            
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            # تحديد الاتجاه
            trend = "صاعد ↑" if curr_p > ema200 else "هابط ↓"
            
            # منطق الإشارة والجودة
            icon, status, row_class, quality = "⚪", "هدوء", "row-calm", "-"
            
            if m_val > s_val:
                row_class = "row-green"
                status = "كول قوي" if v_ratio > 1.2 else "كول"
                icon = "انفجار 🚀" if v_ratio > 1.2 else "🟢"
                quality = "ممتازة ✅" if trend == "صاعد ↑" else "عكس التيار ⚠️"
                if v_ratio > 1.2: sound_triggered = True
            elif m_val < s_val:
                row_class = "row-red"
                status = "بوت قوي" if v_ratio > 1.2 else "بوت"
                icon = "انفجار 📉" if v_ratio > 1.2 else "🔴"
                quality = "ممتازة ✅" if trend == "هابط ↓" else "عكس التيار ⚠️"
                if v_ratio > 1.2: sound_triggered = True

            results.append({
                "⚡": icon, "S": sym, "CH": f"{change_pct:+.2f}%", 
                "P": f"{curr_p:.2f}", "FLT": f"{trend} | RSI:{int(rsi_val)}", 
                "Q": quality, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val
            })

    st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار القناص الاحترافي V42.1 💎</h1>", unsafe_allow_html=True)
    
    col_leg, col_tab = st.columns([1, 5])

    with col_leg:
        st.markdown("""
            <div class="legend-box">
                <h5 style="margin:0 0 10px 0; border-bottom:2px solid black;">دليل المحترفين</h5>
                <div class="leg-item">✅ <b>ممتازة:</b> متوافقة مع الاتجاه</div>
                <div class="leg-item">⚠️ <b>تحذير:</b> عكس اتجاه السوق</div>
                <div class="leg-item"><b>RSI > 70:</b> منطقة خطر (قمة)</div>
                <div class="leg-item"><b>RSI < 30:</b> منطقة ارتداد (قاع)</div>
                <hr style="border-top:2px solid black;">
                <div class="leg-item"><div class="leg-color" style="background-color:#22c55e;"></div> كول (صعود)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ef4444;"></div> بوت (هبوط)</div>
            </div>
        """, unsafe_allow_html=True)

    with col_tab:
        if results:
            html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>الفلتر (EMA|RSI)</th><th>الجودة</th><th>IV</th></tr></thead><tbody>"
            for r in results:
                iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
                html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['CH']}</td><td>{r['P']}</td><td>{r['FLT']}</td><td>{r['Q']}</td><td {iv_style}>{r['IV']}</td></tr>"
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
            if sound_triggered: play_beep()
except Exception as e:
    st.info("جاري تحليل السيولة والاتجاهات...")
