import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثواني (10000 مللي ثانية)
st_autorefresh(interval=10000, key="v42_2_ultimate")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- التنسيق البصري المطور: خلفية بيضاء، خط 25، نصوص سوداء ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 99%; }
    .stApp { background-color: white !important; }
    
    .full-width-table { 
        width: 100% !important; 
        border-collapse: collapse; 
        background-color: white;
        border: 4px solid black !important;
    }
    
    th { 
        background-color: #1e293b !important; 
        color: white !important; 
        text-align: center !important; 
        padding: 15px; 
        font-size: 25px !important;
        border: 2px solid black !important;
    }
    
    td { 
        text-align: center !important; 
        font-weight: 900 !important; 
        border: 3px solid black !important; 
        padding: 15px 5px !important; 
        font-size: 25px !important; 
        color: black !important; 
    }
    
    /* ألوان الصفوف الصريحة */
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }   
    .row-white { background-color: #ffffff !important; }
    .iv-blue { background-color: #7dd3fc !important; } 
    
    .legend-box { padding: 15px; border: 4px solid black; border-radius: 10px; background-color: #ffffff; font-size: 20px; color: black; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']
results = []
sound_triggered = False

st.markdown("<h1 style='text-align:center; color:black; font-size: 40px;'>💎 رادار القناص V42.2 (استجابة سريعة) 💎</h1>", unsafe_allow_html=True)

try:
    # جلب البيانات بفريم 5 دقائق لضمان الاستمرارية وعدم فراغ الصفحة
    data = yf.download(STOCKS, period='2d', interval='5m', group_by='ticker', progress=False)
    
    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                # فك تداخل الأعمدة البرمجي
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                curr_p = float(df['Close'].iloc[-1])
                # حساب التغير اليومي الفعلي
                info = yf.Ticker(sym).fast_info
                prev_close = info.get('previous_close', df['Close'].iloc[0])
                change_pct = ((curr_p - prev_close) / prev_close) * 100
                
                # حساب المؤشرات
                rsi_val = ta.rsi(df['Close'], length=14).iloc[-1]
                ema_50 = ta.ema(df['Close'], length=50).iloc[-1]
                
                # منطق الاستباق (Squeeze)
                bb = ta.bbands(df['Close'], length=20)
                width = (bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0']
                is_squeeze = width.iloc[-1] < width.rolling(20).mean().iloc[-1]
                
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                iv_val = df['Close'].pct_change().std() * np.sqrt(252 * 78) * 100
                
                trend = "صاعد ↑" if curr_p > ema_50 else "هابط ↓"
                icon, row_class, quality = "⚪", "row-white", "-"
                
                # إشارة الاستباق
                pre = "⚡" if (is_squeeze and v_ratio > 1.05) else ""

                if rsi_val > 52:
                    row_class, icon = "row-green", ("انفجار 🚀" if v_ratio > 1.2 else "🟢")
                    quality = "ممتازة ✅" if trend == "صاعد ↑" else "عكس التيار ⚠️"
                    if v_ratio > 1.2: sound_triggered = True
                elif rsi_val < 48:
                    row_class, icon = "row-red", ("انفجار 📉" if v_ratio > 1.2 else "🔴")
                    quality = "ممتازة ✅" if trend == "هابط ↓" else "عكس التيار ⚠️"
                    if v_ratio > 1.2: sound_triggered = True

                results.append({
                    "⚡": f"{pre}{icon}", "S": sym, "CH": f"{change_pct:+.2f}%", 
                    "P": f"{curr_p:.2f}", "FLT": f"{trend} | RSI:{int(rsi_val)}", 
                    "Q": quality, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val
                })
        except: continue

    col_leg, col_tab = st.columns([1, 6])
    
    with col_leg:
        st.markdown("""
            <div class="legend-box">
                <b>دليل القناص</b><br>
                ✅ ممتازة: مع التيار<br>
                ⚠️ مخاطرة: عكس التيار<br>
                ⚡ استباق سيولة<br>
                <hr style="border:1px solid black">
                🔵 عقود IV منخفض
            </div>
        """, unsafe_allow_html=True)

    with col_tab:
        if results:
            html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>الفلتر</th><th>الجودة</th><th>IV</th></tr></thead><tbody>"
            for r in results:
                iv_s = "class='iv-blue'" if r['iv_val_num'] < 15 else ""
                html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['CH']}</td><td>{r['P']}</td><td>{r['FLT']}</td><td>{r['Q']}</td><td {iv_s}>{r['IV']}</td></tr>"
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
            if sound_triggered: play_beep()
        else:
            st.warning("جاري الاتصال بالسوق.. انتظر 10 ثوانٍ للتحديث")

except Exception as e:
    st.error(f"يتم الآن إعادة الاتصال..")
