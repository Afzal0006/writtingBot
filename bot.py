from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import asyncio

# ==== CONFIG ====
BOT_TOKEN = "8350094964:AAF0dQSjrBtBeSTGpUC2z5DOFo-U9_oJhBc"

# ==== GAME STATE ====
games = {}  # chat_id : {players: [], turn: 0, last_word: "", used_words: []}

# ==== COMMANDS ====

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in games:
        await update.message.reply_text("Game already running in this chat!")
        return

    games[chat_id] = {"players": [], "turn": 0, "last_word": "", "used_words": []}
    await update.message.reply_text(
        "Word Duel started! Players, join with /join"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("No game running. Start with /startgame")
        return

    if user.id in games[chat_id]["players"]:
        await update.message.reply_text("You already joined!")
        return

    games[chat_id]["players"].append(user.id)
    await update.message.reply_text(f"{user.first_name} joined the game!")

async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games or len(games[chat_id]["players"]) < 2:
        await update.message.reply_text("Need at least 2 players to start!")
        return

    first_word = random.choice(["apple", "banana", "computer", "telegram", "python"])
    games[chat_id]["last_word"] = first_word
    games[chat_id]["used_words"].append(first_word)
    games[chat_id]["turn"] = 0
    await update.message.reply_text(
        f"Game begins! First word is: {first_word}\n"
        f"{await context.bot.get_chat(games[chat_id]['players'][0])} your turn! Send a word starting with '{first_word[-1]}'"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.lower()

    if chat_id not in games:
        return

    game = games[chat_id]
    if user.id != game["players"][game["turn"]]:
        await update.message.reply_text("Wait for your turn!")
        return

    if text[0] != game["last_word"][-1]:
        await update.message.reply_text(f"Word must start with '{game['last_word'][-1]}'")
        return

    if text in game["used_words"]:
        await update.message.reply_text("Word already used!")
        return

    game["last_word"] = text
    game["used_words"].append(text)
    game["turn"] = (game["turn"] + 1) % len(game["players"])

    next_player_id = game["players"][game["turn"]]
    next_player = await context.bot.get_chat(next_player_id)
    await update.message.reply_text(
        f"Good! Next word is {text[-1]}.\n{next_player.first_name}, your turn!"
    )

async def endgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in games:
        del games[chat_id]
        await update.message.reply_text("Game ended.")

# ==== MAIN ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("startgame", startgame))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("begin", begin))
    app.add_handler(CommandHandler("endgame", endgame))
    app.add_handler(CommandHandler("play", play))
    app.run_polling()

if __name__ == "__main__":
    main()
