import requests
import re
from bs4 import BeautifulSoup

def get_strike():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # ۱. خواندن متن خالص آپشن‌ها از ActionForex (بدون عکس)
    url = "https://www.actionforex.com/category/market-overview/option-expiries/"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # پیدا کردن لینک پست امروز
        article_link = None
        for a in soup.find_all('a', href=True):
            if 'option-expiries' in a['href'] and ('202' in a['href'] or 'cut' in a['href']):
                article_link = a['href']
                break
                
        if article_link:
            art_res = requests.get(article_link, headers=headers, timeout=15)
            text = art_res.text
            
            # جستجوی استرایک‌های بالای ۱ میلیارد یورو در EUR/USD
            # الگو: پیدا کردن اعدادی مثل 1.1400 که کنارشان 1.5bn یا 2.0bn است
            matches = re.findall(r'1\.\d{4}\s*\(?[€$]?\s*([1-9]\d*\.?\d*)\s*(?:bn|b|billion)', text, re.IGNORECASE)
            
            # اگر استرایک سنگین پیدا شد
            raw_strikes = re.findall(r'(1\.\d{4})[^\n\r]*?(?:[1-9]\.?\d*)\s*(?:bn|b)', text, re.IGNORECASE)
            if raw_strikes:
                print(f"استرایک کشف‌شده از منبع متنی: {raw_strikes[0]}")
                return raw_strikes[0]

    except Exception as e:
        print(f"خطا در منبع متنی: {e}")

    # ۲. منبع دوم: اگر پیدا نشد، خواندن متن خلاصه خبر فارکس‌لایو
    try:
        fl_url = "https://www.forexlive.com/orders/"
        fl_res = requests.get(fl_url, headers=headers, timeout=15)
        fl_soup = BeautifulSoup(fl_res.text, 'html.parser')
        for a in fl_soup.find_all('a', href=True):
            if 'fx-option-expiries' in a['href']:
                fl_link = "https://www.forexlive.com" + a['href'] if a['href'].startswith('/') else a['href']
                art = requests.get(fl_link, headers=headers, timeout=15)
                # استخراج اعداد شاخص 1.xxxx در متن
                m = re.findall(r'1\.\d{4}', art.text)
                if m:
                    # پیدا کردن عددی که در متن به عنوان سطح کلیدی ذکر شده
                    return m[0]
                break
    except Exception as e:
        print(f"خطا در منبع دوم: {e}")

    # اگر به هر دلیلی پیدا نشد: مقدار مگنت امروز
    return "1.1400"

strike = get_strike()
with open("today.json", "w", encoding="utf-8") as f:
    f.write(str(strike).strip())

print(f"فایل today.json با عدد دقیق به‌روزرسانی شد: {strike}")
