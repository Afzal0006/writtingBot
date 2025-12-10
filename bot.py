import time
import threading
import requests
from bs4 import BeautifulSoup

TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"
URL = "https://api.telegram.org/bot" + TOKEN
CHAT_ID = "-1002760813128"

GIFTS_URL = "https://marketapp.ws/gifts/?tab=history"
CHECK_INTERVAL = 30

last_item = None
last_update_id = 0


def fetch_gifts():
    r = requests.get(GIFTS_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.find_all(["div", "tr"])
    data = []

    for row in rows:
        text = row.get_text(" ", strip=True)
        if text and any(k in text.lower() for k in ["gift", "sell", "₹", "$"]):
            data.append(text)

    return data[:20]


def send_message(chat, text):
    try:
        requests.get(URL + "/sendMessage", params={"chat_id": chat, "text": text})
    except:
        pass


def handle_update(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        gifts = fetch_gifts()
        if not gifts:
            send_message(chat_id, "No data found.")
        else:
            msg = "Latest 10 Gifts:\n\n" + "\n".join("• " + g for g in gifts[:10])
            send_message(chat_id, msg)


def poll_telegram():
    global last_update_id

    while True:
        try:
            r = requests.get(URL + "/getUpdates", params={"offset": last_update_id + 1})
            data = r.json()

            if "result" in data:
                for update in data["result"]:
                    last_update_id = update["update_id"]

                    if "message" in update:
                        handle_update(update["message"])

        except Exception as e:
            print("Polling Error:", e)

        time.sleep(1)


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
                    send_message(CHAT_ID, f"New Gift Sold:\n{newest}")

        except Exception as e:
            print("Monitor Error:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=poll_telegram, daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()

    print("BOT RUNNING...")
    while True:
        time.sleep(10)
