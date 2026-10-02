
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup

def fetch_eurusd_option_strike():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("🔍 در حال جستجوی گزارش روزانه آپشن‌های ۱۰ صبح نیویورک...")
    search_url = "https://www.forexlive.com/Orders"
    response = requests.get(search_url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"خطای دسترسی به سایت: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    
    article_link = None
    for a in soup.find_all('a', href=True):
        if "fx-option-expiries" in a['href'].lower() or "option-expiries-for-10am" in a['href'].lower():
            article_link = "https://www.forexlive.com" + a['href']
            break

    if not article_link:
        article_link = "https://www.forexlive.com/orders"

    article_resp = requests.get(article_link, headers=headers, timeout=10)
    article_soup = BeautifulSoup(article_resp.text, 'html.parser')
    text_content = article_soup.get_text()

    eur_matches = re.search(r'EUR/USD\s*:\s*(.*?)(?:\n|GBP/USD|USD/JPY)', text_content, re.IGNORECASE)
    
    selected_strike = 1.0850 
    max_volume_bn = 0.0

    if eur_matches:
        eur_line = eur_matches.group(1)
        print(f"📊 خط دیتای یورو پیدا شد: {eur_line}")
        
        items = re.findall(r'(\d+\.\d{2,4})\s*\(([\d\.]+)\s*([BMbm])\)', eur_line)
        for strike_str, vol_str, unit in items:
            strike = float(strike_str)
            vol = float(vol_str)
            vol_in_billion = vol if unit.upper() == 'B' else (vol / 1000.0)
            
            if vol_in_billion > max_volume_bn:
                max_volume_bn = vol_in_billion
                selected_strike = strike

    print(f"🎯 استرایک منتخب امروز با بیشترین حجم ({max_volume_bn:.2f}B$): {selected_strike}")
    
    output_data = {
        "strike": selected_strike,
        "pair": "EURUSD",
        "volume_billion": round(max_volume_bn, 2),
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "updated_utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print("✅ فایل today.json با موفقیت آپدیت شد.")

if __name__ == "__main__":
    fetch_eurusd_option_strike()
