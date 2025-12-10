import time
import threading
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler

BOT_TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"
CHAT_ID = -1002760813128
URL = "https://marketapp.ws/gifts/?tab=history"
CHECK_INTERVAL = 3

bot = Bot(BOT_TOKEN)
last_item = None


def fetch_gifts():
    r = requests.get(URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.find_all(["div", "tr"])
    data = []

    for row in rows:
        text = row.get_text(" ", strip=True)
        if text and any(x in text.lower() for x in ["gift", "sell", "₹", "$"]):
            data.append(text)

    return data[:20]


def start(update: Update, context):
    gifts = fetch_gifts()
    if not gifts:
        update.message.reply_text("No data found.")
        return

    msg = "Latest 10 Gifts:\n\n" + "\n".join("• " + g for g in gifts[:10])
    update.message.reply_text(msg)


def monitor():
    global last_item

    while True:
        try:
            gifts = fetch_gifts()
            if gifts:
                newest = gifts[0]

                if last_item is None:
                    last_item = newest
                elif newest != last_item:
                    last_item = newest
                    bot.send_message(chat_id=CHAT_ID, text=f"New Gift Sold:\n{newest}")

        except Exception as e:
            print("Monitor Error:", e)

        time.sleep(CHECK_INTERVAL)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    threading.Thread(target=monitor, daemon=True).start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
