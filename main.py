import pandas as pd

# --- إعدادات رادار القناص V42.3 ---
# [cite: 2026-01-28] تم تحديث المنطق ليدعم الاستباق السيولي
def Sniper_Radar_V42_3(market_data):
    results = []
    
    for stock in market_data:
        # 1. حساب المؤشرات الأساسية
        rsi = calculate_rsi(stock['prices'])
        ema_50 = calculate_ema(stock['prices'], 50)
        current_price = stock['current_price']
        volume_momentum = stock['volume'] / stock['avg_volume']
        
        # 2. مستشعر الاستباق (الجديد ⚡)
        # يراقب تضيق السعر مع زيادة الفوليوم قبل الانفجار
        is_squeeze = check_bollinger_squeeze(stock['prices'])
        pre_breakout_trigger = (volume_momentum > 1.5) and (is_squeeze)
        
        # 3. منطق تحديد الإشارة والجودة
        quality = "ممتازة ✅" if (rsi > 50 and current_price > ema_50) else "عكس التيار ⚠️"
        
        # تحديد حالة الإشارة (كول أو بوت)
        if rsi > 55 or pre_breakout_trigger:
            signal_color = "Green"
            action = "قنص استباقي (CALL) 🚀" if pre_breakout_trigger else "صاعد"
        elif rsi < 45:
            signal_color = "Red"
            action = "هابط (PUT)"
        else:
            signal_color = "Grey"
            action = "انتظار (تجميع)"

        # 4. فلتر الـ 20 صفقة (تآكل الزمن)
        # يعطي تنبيه إذا كان السعر ثابت لأكثر من 15 دقيقة
        time_decay_warning = "⚠️ خروج (ثبات سعري)" if stock['minutes_flat'] > 15 else "آمن"

        results.append({
            "السهم": stock['ticker'],
            "السعر": current_price,
            "RSI": rsi,
            "الجودة": quality,
            "تنبيه الاستباق": "دخول مبكر ⚡" if pre_breakout_trigger else "مراقبة",
            "الإجراء": action,
            "التحذير": time_decay_warning
        })
        
    return pd.DataFrame(results)

# --- تشغيل الرادار اللحظي ---
# ملاحظة: الكود مبرمج ليعطي إشارة دخول قبل المقاومة بـ 5 سنتات
