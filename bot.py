from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"

# Queue for waiting users
waiting_users = []
active_chats = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Anonymous Chat!\n\n"
        "Use /find to search for a partner.\n"
        "Use /stop to end chat.\n"
        "Use /next to find a new partner."
    )

# Find partner
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        await update.message.reply_text("✅ You are already chatting. Use /stop first to leave.")
        return

    if waiting_users and waiting_users[0] != user_id:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        await context.bot.send_message(partner_id, "✅ Connected! You are now chatting anonymously.\nType /next or /stop anytime.")
        await update.message.reply_text("✅ Connected! You are now chatting anonymously.\nType /next or /stop anytime.")
    else:
        if user_id not in waiting_users:
            waiting_users.append(user_id)
        await update.message.reply_text("⌛ Searching for a partner... Please wait.")

# Stop chat
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await context.bot.send_message(partner_id, "❌ Your partner has left the chat.")
        await update.message.reply_text("❌ You left the chat.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("❌ You stopped searching.")
    else:
        await update.message.reply_text("❌ You are not in a chat or queue.")

# Next partner
async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stop(update, context)
    await find(update, context)

# Forward messages
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        if update.message.text:
            await context.bot.send_message(partner_id, update.message.text)
        elif update.message.photo:
            await context.bot.send_photo(partner_id, update.message.photo[-1].file_id, caption=update.message.caption)
        elif update.message.sticker:
            await context.bot.send_sticker(partner_id, update.message.sticker.file_id)
        elif update.message.voice:
            await context.bot.send_voice(partner_id, update.message.voice.file_id)
        elif update.message.video:
            await context.bot.send_video(partner_id, update.message.video.file_id, caption=update.message.caption)

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("next", next_partner))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward))

    app.run_polling()

if __name__ == "__main__":
    main()
