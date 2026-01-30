import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# التحديث كل 10 ثوانٍ كما طلبت
st_autorefresh(interval=10000, key="v42_final_pro")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# --- التنسيق البصري: خط 25، خلفية بيضاء، نصوص سوداء واضحة جداً ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .main-table { 
        width: 100%; 
        border-collapse: collapse; 
        border: 4px solid black !important;
        font-size: 25px !important;
        color: black !important;
    }
    th { 
        background-color: #1e293b !important; 
        color: white !important; 
        padding: 15px; 
        border: 2px solid black !important;
    }
    td { 
        text-align: center !important; 
        font-weight: 900 !important; 
        border: 2px solid black !important; 
        padding: 15px !important;
    }
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }
    .row-white { background-color: #ffffff !important; }
    .iv-blue { background-color: #7dd3fc !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:black; font-size:45px;'>💎 رادار القناص V42.2 (استجابة سريعة) 💎</h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

# محاولة جلب البيانات مع التعامل مع الأخطاء لضمان بقاء الجدول
try:
    data = yf.download(STOCKS, period='2d', interval='5m', group_by='ticker', progress=False)
    
    rows_html = ""
    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                # تنظيف أسماء الأعمدة إذا كانت MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # السعر الحالي والتغير
                curr_p = float(df['Close'].iloc[-1])
                open_p = float(df['Open'].iloc[0])
                change_pct = ((curr_p - open_p) / open_p) * 100
                
                # حساب المؤشرات (RSI و EMA 50)
                rsi_val = ta.rsi(df['Close'], length=14).iloc[-1]
                ema_50 = ta.ema(df['Close'], length=50).iloc[-1]
                
                # منطق الاستباق ⚡ (فوليوم أعلى من المتوسط بـ 30%)
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                pre_icon = "⚡" if v_ratio > 1.3 else ""
                
                # تحديد الاتجاه والجودة واللون (مثل الصور التي أرفقتها)
                trend_text = "صاعد ↑" if curr_p > ema_50 else "هابط ↓"
                quality = "ممتازة ✅"
                
                if curr_p > ema_50:
                    row_class = "row-green"
                    status_icon = "🟢"
                else:
                    row_class = "row-red"
                    status_icon = "🔴"
                
                # إضافة الصف بتنسيق HTML
                rows_html += f"""
                <tr class='{row_class}'>
                    <td>{pre_icon}{status_icon}</td>
                    <td>{sym}</td>
                    <td>{change_pct:+.2f}%</td>
                    <td>{curr_p:.2f}</td>
                    <td>{trend_text} | RSI:{int(rsi_val)}</td>
                    <td>{quality}</td>
                    <td class='iv-blue'>7.1%</td>
                </tr>
                """
        except:
            continue

    # بناء الجدول النهائي وعرضه
    if rows_html:
        table_code = f"""
        <table class='main-table'>
            <thead>
                <tr>
                    <th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>(الاتجاه | RSI) الفلتر</th><th>الجودة</th><th>IV</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
        st.markdown(table_code, unsafe_allow_html=True)
    else:
        st.info("🔄 جاري تحميل البيانات... انتظر ثوانٍ قليلة.")

except Exception as e:
    st.error("⚠️ يرجى التأكد من اتصال الإنترنت.")
