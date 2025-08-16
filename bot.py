from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"

# Store whispers {whisper_id: {"text": ..., "target_username": ...}}
whispers = {}

# Handle group messages starting with @afz
async def handle_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.lower().startswith("@afz "):
        return

    parts = text.split()
    if len(parts) < 3:
        await update.message.reply_text("❌ Format: @afz <message> @username")
        return

    target_username = parts[-1]  # last word should be @username
    if not target_username.startswith("@"):
        await update.message.reply_text("❌ Format: @afz <message> @username")
        return

    # Secret message = all words between @afz and @username
    secret_text = " ".join(parts[1:-1])

    whisper_id = str(update.message.message_id)
    whispers[whisper_id] = {"text": secret_text, "target_username": target_username.lower()}

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"🔑 Open Whisper for {target_username}", callback_data=f"whisper:{whisper_id}")]]
    )

    await update.message.reply_text(
        f"🤫 Whisper created for {target_username}", reply_markup=button
    )

# Handle button click
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("whisper:"):
        return

    whisper_id = query.data.split(":")[1]
    if whisper_id not in whispers:
        await query.answer("❌ Whisper not found!", show_alert=True)
        return

    whisper = whispers[whisper_id]
    target_username = whisper["target_username"]
    secret_text = whisper["text"]

    user_username = "@" + query.from_user.username if query.from_user.username else None

    if user_username and user_username.lower() == target_username:
        await query.answer(f"💌 Secret: {secret_text}", show_alert=True)
    else:
        await query.answer("🚫 This whisper is not for you!", show_alert=True)

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_whisper))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
