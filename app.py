import requests
from bs4 import BeautifulSoup
import telebot
import time
import re

# =====================
# НАСТРОЙКИ
# =====================

BOT_TOKEN = ""
CHAT_ID = ""

URL = "https://funpay.com/lots/1355/"
PRICE_LIMIT = 200

CHECK_INTERVAL = 120  # секунд

bot = telebot.TeleBot(BOT_TOKEN)

seen = set()


def parse_price(text):
    text = text.replace("₽", "").replace(" ", "")
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


def get_lots():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()

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

        except Exception:
            pass

    return lots


def check():
    global seen

    lots = get_lots()

    for lot in lots:
        if lot["price"] is None:
            continue

        if lot["price"] < PRICE_LIMIT:

            lot_id = f'{lot["title"]}_{lot["price"]}'

            if lot_id not in seen:
                seen.add(lot_id)

                msg = (
                    f"🔥 Найден дешевый лот!\n\n"
                    f"💰 Цена: {lot['price']} ₽\n"
                    f"📦 {lot['title']}\n"
                    f"🔗 {lot['link']}"
                )

                bot.send_message(CHAT_ID, msg)


if __name__ == "__main__":
    print("Bot started")

    while True:
        try:
            check()
        except Exception as e:
            print("ERROR:", e)

        time.sleep(CHECK_INTERVAL)