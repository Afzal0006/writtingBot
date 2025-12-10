import time
import threading
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient, events

API_ID = 24526311
API_HASH = "717d5df262e474f88d86c537a787c98d"
BOT_TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"

GIFTS_URL = "https://marketapp.ws/gifts/?tab=history"
CHECK_INTERVAL = 30

last_item = None

client = TelegramClient('session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


# -----------------------------
# Gift Scraper
# -----------------------------
def fetch_gifts():
    r = requests.get(GIFTS_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.find_all(["div", "tr", "li", "span"])

    items = []
    for row in rows:
        text = row.get_text(" ", strip=True)
        if len(text) > 5:
            if any(k in text.lower() for k in ["gift", "sell", "₹", "$"]):
                items.append(text)

    return items[:20]


# -----------------------------
# /start command
# -----------------------------
@client.on(events.NewMessage(pattern="/start"))
async def start_command(event):
    gifts = fetch_gifts()

    if not gifts:
        await event.reply("No gift history found!")
        return

    msg = "🛒 **Latest 10 Sold Gifts:**\n\n"
    for g in gifts[:10]:
        msg += f"• {g}\n"

    await event.reply(msg)


# -----------------------------
# Background Monitor
# -----------------------------
async def monitor():
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
                    await client.send_message(
                        entity=event.chat_id,
                        message=f"🆕 **New Gift Sold:**\n{newest}"
                    )
        except Exception as e:
            print("Monitor Error:", e)

        time.sleep(CHECK_INTERVAL)


# -----------------------------
# Start Monitor Thread
# -----------------------------
def start_monitor():
    loop = client.loop
    loop.create_task(monitor())


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=start_monitor, daemon=True).start()
    print("BOT RUNNING…")
    client.run_until_disconnected()
