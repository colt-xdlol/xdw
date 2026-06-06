import requests
from bs4 import BeautifulSoup
import re
import time
import os
from datetime import datetime

URL = "https://funpay.com/lots/1355/"
PRICE_LIMIT = 200
CHECK_INTERVAL = 120

BOT_TOKEN = "6228569579:AAEWA4c9OoT9Ox6xfihmrGDsD4OufokzZxM"
CHAT_ID = "5684330880"

seen = set()

def parse_price(text):
    text = text.replace("₽", "").replace(" ", "")
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None

def get_lots():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    lots = []
    for lot in soup.select(".tc-item"):
        try:
            title_el = lot.select_one(".tc-desc-text")
            price_el = lot.select_one(".tc-price")

            if not title_el or not price_el:
                continue

            title = title_el.get_text(" ", strip=True)
            price = parse_price(price_el.text)

            link = lot.get("href")
            if link and link.startswith("/"):
                link = "https://funpay.com" + link

            lots.append({
                "title": title,
                "price": price,
                "link": link
            })
        except:
            continue

    return lots

def git_push():
    os.system("git add deals.md")
    os.system('git commit -m "update deals" || exit 0')
    os.system("git push")

def main():
    lots = get_lots()

    with open("deals.md", "a", encoding="utf-8") as f:
        for lot in lots:
            if lot["price"] is None:
                continue

            if lot["price"] < PRICE_LIMIT:
                line = f"{datetime.utcnow()} | {lot['price']} | {lot['title']} | {lot['link']}\n"
                f.write(line)
                print("NEW:", line.strip())

    git_push()

if __name__ == "__main__":
    print("Bot started")

    while True:
        try:
            main()
        except Exception as e:
            print("ERROR:", e)

        time.sleep(CHECK_INTERVAL)
