from pyrogram import Client, filters
from PIL import Image, ImageDraw, ImageFont
import io

# -------------------------------
# Apna BOT_TOKEN yahan daalein
BOT_TOKEN = "8051082366:AAECqW7-a_x135g2iDpUG7-1_eYowURM7Bw"
# -------------------------------

app = Client("write_bot", bot_token=BOT_TOKEN)

@app.on_message(filters.command("write") & filters.private)
async def write_text(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /write Your text here")
        return

    text = " ".join(message.command[1:])
    
    # Create white image
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font settings
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_width, text_height = draw.textsize(text, font=font)
    position = ((800 - text_width)//2, (400 - text_height)//2)
    
    draw.text(position, text, fill="black", font=font)
    
    # Save image to bytes
    bio = io.BytesIO()
    bio.name = "image.png"
    img.save(bio, 'PNG')
    bio.seek(0)
    
    # Send image
    await message.reply_photo(photo=bio)

print("Bot is running...")
app.run()
