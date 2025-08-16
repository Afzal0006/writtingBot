from telegram.ext import Application
import asyncio
import json
import os

# === Bot Token directly placed ===
BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"
GROUPS_FILE = "groups.json"

# --- Load saved groups ---
if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "r") as f:
        group_ids = json.load(f)
else:
    group_ids = []

# --- Save groups ---
def save_groups():
    with open(GROUPS_FILE, "w") as f:
        json.dump(group_ids, f)

# --- Startup task to send message to all groups ---
async def send_startup_messages(app: Application):
    await asyncio.sleep(5)
    for gid in group_ids:
        try:
            await app.bot.send_message(chat_id=gid, text="Hlo everyone")
        except Exception as e:
            print(f"Failed to send message to {gid}: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.run_task(send_startup_messages(app))  # Startup task
    print("🤖 Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
