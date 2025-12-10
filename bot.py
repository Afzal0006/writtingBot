import time
import threading
import requests
from bs4 import BeautifulSoup

TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"
CHAT_ID = "-1002760813128"   # group id

API_URL = f"https://api.telegram.org/bot{TOKEN}"
GIFTS_URL = "https://marketapp.ws/gifts/?tab=history"

CHECK_INTERVAL = 30
last_item = None
last_update_id = 0


# -----------------------------
# SEND TELEGRAM MESSAGE
# -----------------------------
def send_message(chat, text):
    try:
        requests.get(API_URL + "/sendMessage", params={"chat_id": chat, "text": text})
    except:
        pass


# -----------------------------
# SCRAPING FUNCTION
# -----------------------------
def fetch_gifts():
    r = requests.get(GIFTS_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.find_all(["tr", "div", "li", "span"])
    items = []

    for row in rows:
        text = row.get_text(" ", strip=True)
        if len(text) > 5:
            if any(k in text.lower() for k in ["gift", "sell", "₹", "$"]):
                items.append(text)

    return items[:20]


# -----------------------------
# HANDLE /start
# -----------------------------
def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text == "/start":
        gifts = fetch_gifts()

        if not gifts:
            send_message(chat_id, "No data found.")
            return

        send_message(chat_id, "Latest 10 Gifts:\n\n" + "\n".join("• " + g for g in gifts[:10]))


# -----------------------------
# POLLING UPDATES
# -----------------------------
def poll_updates():
    global last_update_id

    while True:
        try:
            r = requests.get(API_URL + "/getUpdates", params={"offset": last_update_id + 1})
            data = r.json()

            if "result" in data:
                for upd in data["result"]:
                    last_update_id = upd["update_id"]

                    if "message" in upd:
                        handle_message(upd["message"])

        except Exception as e:
            print("Polling error:", e)

        time.sleep(1)


# -----------------------------
# AUTO NEW SELL MONITOR
# -----------------------------
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
            print("Monitor error:", e)

        time.sleep(CHECK_INTERVAL)


# -----------------------------
# START BOT
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=poll_updates, daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()

    print("BOT RUNNING...")
    while True:
        time.sleep(10)
