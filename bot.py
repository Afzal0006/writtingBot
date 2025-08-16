from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import json
import os

# === Bot Token ===
BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"
GROUPS_FILE = "groups.json"

# --- Load already known groups ---
if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "r") as f:
        group_ids = json.load(f)
else:
    group_ids = []

# --- Save groups ---
def save_groups():
    with open(GROUPS_FILE, "w") as f:
        json.dump(group_ids, f)

# --- Auto welcome message on startup ---
async def send_startup_messages(app):
    await asyncio.sleep(5)  # thoda wait
    # Send message to all known groups
    for gid in group_ids:
        try:
            await app.bot.send_message(chat_id=gid, text="Hello everyone")
        except:
            pass

# --- Track new groups bot joins ---
async def new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"] and chat.id not in group_ids:
        group_ids.append(chat.id)
        save_groups()
        # Optional: immediately send message to new group
        try:
            await context.bot.send_message(chat.id, "Hello everyone")
        except:
            pass

# --- Optional: respond to /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands & message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group))

    # Startup task
    app.post_init(send_startup_messages)

    print("🤖 Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
