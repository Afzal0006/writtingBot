from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import re

BOT_TOKEN = "8411607342:AAHSDSB98MDYeuYMZUk6nHqKtZy2zquhVig"

whispers = {}

async def whisper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match = re.match(r"@afzWhisperBot\s+(.+)\s+(@\w+)", text, re.IGNORECASE)
    if not match:
        return

    message, username = match.groups()
    chat_id = update.effective_chat.id
    msg_id = update.message.id

    whispers[f"{chat_id}:{msg_id}"] = {"message": message, "username": username.lower()}

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔒 Whisper for {username} 📩 View",
                              callback_data=f"whisper:{chat_id}:{msg_id}")]
    ])

    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=button,
        text="👇 Whisper created (only recipient can open)"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("whisper:"):
        return

    _, chat_id, msg_id = data.split(":")
    key = f"{chat_id}:{msg_id}"

    if key not in whispers:
        return await query.edit_message_text("❌ Whisper expired.")

    whisper_data = whispers[key]
    message = whisper_data["message"]
    target_username = whisper_data["username"]

    user = query.from_user
    if user.username and ("@" + user.username.lower()) == target_username:
        try:
            await context.bot.send_message(user.id, f"🔒 Whisper for you:\n\n{message}")
            await query.edit_message_text("✅ Whisper delivered in your DM!")
        except:
            await query.edit_message_text("⚠️ Please start the bot in DM to receive whispers.")
    else:
        await query.answer("❌ This whisper is not for you!", show_alert=True)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, whisper_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🤖 afzWhisperBot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
