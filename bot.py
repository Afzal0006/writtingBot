from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from pymongo import MongoClient
from datetime import datetime
import asyncio

# ===== CONFIG =====
BOT_TOKEN = "8411607342:AAHSDSB98MDYeuYMZUk6nHqKtZy2zquhVig"
MONGO_URI = "mongodb+srv://afzal99550:afzal99550@cluster0.aqmbh9q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "habit_bot"
COLLECTION_NAME = "reminders"

# ===== MongoDB Setup =====
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ===== /start command =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("❓ Help", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Hello! I am your Habit Reminder Bot.\n"
        "Click the Help button below to see all commands.",
        reply_markup=reply_markup
    )

# ===== /help command =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *Available Commands:*\n\n"
        "/start - Start the bot and get instructions\n"
        "/add HH:MM AM/PM Task - Add a reminder\n"
        "   Example: /add 2:30 PM Gym\n"
        "/list - List all your reminders\n"
        "/delete - Delete a reminder (or use the button in /list)\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===== /add command =====
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /add HH:MM AM/PM Task\nExample: /add 2:30 PM Gym")
        return
    
    time_str = f"{context.args[0]} {context.args[1]}"  # "2:30 PM"
    task = " ".join(context.args[2:])
    
    try:
        # Convert 12-hour to 24-hour format
        time_24 = datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        await update.message.reply_text("Time format is wrong! Use HH:MM AM/PM")
        return
    
    collection.insert_one({
        "user_id": user_id,
        "task": task,
        "time": time_24,
        "recurring": True  # daily recurring
    })
    
    await update.message.reply_text(f"✅ Reminder added for {time_str}: {task}")

# ===== /list command =====
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reminders = list(collection.find({"user_id": user_id}))
    if not reminders:
        await update.message.reply_text("You have no reminders.")
        return
    
    text = "⏰ Your reminders:\n"
    keyboard = []
    for r in reminders:
        time_12 = datetime.strptime(r["time"], "%H:%M").strftime("%I:%M %p")
        text += f"{time_12} - {r['task']}\n"
        keyboard.append([InlineKeyboardButton(f"Delete: {r['task']}", callback_data=str(r['_id']))])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===== Button callback (delete & help) =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await help_command(update, context)
    else:
        # Delete reminder by _id
        from bson import ObjectId
        collection.delete_one({"_id": ObjectId(query.data)})
        await query.edit_message_text("✅ Reminder deleted!")

# ===== Reminder Checker =====
async def reminder_checker(app: Application):
    while True:
        now = datetime.now().strftime("%H:%M")
        reminders = collection.find({"time": now})
        for r in reminders:
            try:
                await app.bot.send_message(r["user_id"], f"⏰ Reminder: {r['task']}")
            except:
                pass
        await asyncio.sleep(60)

# ===== MAIN =====
app = Application.builder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list_reminders))
app.add_handler(CallbackQueryHandler(button_callback))

# Run reminder checker in background
app.job_queue.run_repeating(lambda ctx: asyncio.create_task(reminder_checker(app)), interval=60, first=10)

print("Bot started...")
app.run_polling()
