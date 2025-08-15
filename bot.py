from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

BOT_TOKEN = "8350094964:AAGhPKz3r5902YEDKsWM6DBqHVLttkp4ux8"

# Enable logging
logging.basicConfig(level=logging.INFO)

# ==== GAME STATE ====
games = {}  # chat_id : {"board": [' ']*9, "players": [player1_id, player2_id], "turn": 0}

# ==== HELPER FUNCTIONS ====
def display_board(board):
    return (
        f"{board[0]} | {board[1]} | {board[2]}\n"
        "---------\n"
        f"{board[3]} | {board[4]} | {board[5]}\n"
        "---------\n"
        f"{board[6]} | {board[7]} | {board[8]}"
    )

def check_winner(board):
    combos = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for c in combos:
        if board[c[0]] == board[c[1]] == board[c[2]] != ' ':
            return True
    return False

def board_full(board):
    return ' ' not in board

# ==== COMMANDS ====
async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in games:
        await update.message.reply_text("Game already running!")
        return
    games[chat_id] = {"board": [' ']*9, "players": [], "turn": 0}
    await update.message.reply_text("Tic-Tac-Toe started! Two players join with /join")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("No game running. Start with /startgame")
        return
    game = games[chat_id]
    if len(game["players"]) >= 2:
        await update.message.reply_text("Already 2 players joined!")
        return
    if user.id in game["players"]:
        await update.message.reply_text("You already joined!")
        return
    game["players"].append(user.id)
    await update.message.reply_text(f"{user.first_name} joined the game!")
    if len(game["players"]) == 2:
        first_player_id = game["players"][game["turn"]]
        await update.message.reply_text(f"Both players joined! <code>{display_board(game['board'])}</code>\nPlayer 1's turn! Use /move &lt;1-9&gt; to play.", parse_mode="HTML")

async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("No game running!")
        return
    game = games[chat_id]
    if len(game["players"]) < 2:
        await update.message.reply_text("Waiting for 2 players to join.")
        return
    if user.id != game["players"][game["turn"]]:
        await update.message.reply_text("Not your turn!")
        return
    try:
        pos = int(context.args[0]) - 1
        if pos < 0 or pos > 8:
            raise ValueError
    except:
        await update.message.reply_text("Use: /move <1-9>")
        return
    if game["board"][pos] != ' ':
        await update.message.reply_text("Position already taken!")
        return
    symbol = 'X' if game["turn"] == 0 else 'O'
    game["board"][pos] = symbol
    if check_winner(game["board"]):
        await update.message.reply_text(f"{user.first_name} wins!\n<code>{display_board(game['board'])}</code>", parse_mode="HTML")
        del games[chat_id]
        return
    elif board_full(game["board"]):
        await update.message.reply_text(f"Game draw!\n<code>{display_board(game['board'])}</code>", parse_mode="HTML")
        del games[chat_id]
        return
    # Next turn
    game["turn"] = 1 - game["turn"]
    next_player_id = game["players"][game["turn"]]
    await update.message.reply_text(f"<code>{display_board(game['board'])}</code>\nNext player's turn!", parse_mode="HTML")

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
    app.add_handler(CommandHandler("move", move))
    app.add_handler(CommandHandler("endgame", endgame))
    app.run_polling()

if __name__ == "__main__":
    main()
