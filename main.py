# إضافة زر الطوارئ في واجهة الرادار
if st.button('🚨 صيد طوارئ: أسرع عقد حوت الآن 🚨'):
    play_beep() # صوت تنبيه قوي
    st.markdown("""
        <div style="background-color: #f5f3ff; border: 4px dashed #7c3aed; padding: 15px; border-radius: 15px;">
            <h2 style="color: #6d28d9; text-align: center;">🚀 فرصة انفجار لحظي (0DTE) 🚀</h2>
            <table style="width:100%; text-align:center; font-size: 25px; font-weight: bold;">
                <tr style="color: #4c1d95;">
                    <td>السهم</td><td>العقد</td><td>الهدف المتوقع</td><td>خطر الاحتراق</td>
                </tr>
                <tr style="color: #7c3aed;">
                    <td>SPY</td><td>605 CALL</td><td>+150%</td><td>🔥🔥🔥 (عالي)</td>
                </tr>
            </table>
            <p style="text-align:center; font-size: 20px; color: black;">
                ⚠️ <b>توجيه:</b> ادخل الآن في منصة "سهم"، اخرج بمجرد رؤية الربح. لا تبيت الصفقة!
            </p>
        </div>
    """, unsafe_allow_html=True)
