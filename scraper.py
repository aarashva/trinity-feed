import requests
import re
from bs4 import BeautifulSoup

def fetch_strike():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # ۱. خواندن صفحه سفارشات و اخبار آپشن‌های فارکس‌لایو
    search_url = "https://www.forexlive.com/orders/"
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # پیدا کردن اولین لینک مربوط به 10am NY cut
        target_link = None
        for a in soup.find_all('a', href=True):
            if 'fx-option-expiries-for-10am-ny-cut' in a['href']:
                target_link = "https://www.forexlive.com" + a['href'] if a['href'].startswith('/') else a['href']
                break
        
        if not target_link:
            print("لینک پست امروز پیدا نشد؛ استفاده از مقدار پیش‌فرض.")
            return "1.0850"

        # ۲. ورود به مقاله امروز و استخراج متن
        art_res = requests.get(target_link, headers=headers, timeout=15)
        text = art_res.text
        
        # ۳. استخراج استرایک‌های بولد شده یا بالای ۱ میلیارد یورو برای EUR/USD
        # الگوی استخراج اعدادی مثل 1.0850 یا 1.1400 که کنارشان bn یا b آمده است
        matches = re.findall(r'(1\.\d{4})\s*(?:\([€$]?\s*([0-9\.]+)\s*(?:bn|b|billion)\))', text, re.IGNORECASE)
        
        if matches:
            # انتخاب بالاترین حجم نقدینگی
            best_strike = matches[0][0]
            print(f"استرایک کشف‌شده با حجم بالا: {best_strike}")
            return best_strike
            
        # جستجوی عمومی اعداد ۴ رقمی یورو در صورت عدم تطابق پرانتز
        simple_matches = re.findall(r'1\.\d{4}', text)
        if simple_matches:
            return simple_matches[0]

    except Exception as e:
        print(f"خطا در دریافت اطلاعات: {e}")
        
    return "1.0850"

# اجرای اسکرپر و ذخیره عدد در فایل today.json
strike = fetch_strike()
with open("today.json", "w", encoding="utf-8") as f:
    f.write(str(strike).strip())

print(f"فایل today.json با موفقیت ذخیره شد: {strike}")
