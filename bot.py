import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_TOKEN = "8350094964:AAF0dQSjrBtBeSTGpUC2z5DOFo-U9_oJhBc"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def make_lined_paper(width=1080, height=1440, margin=60, line_gap=56):
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    box_w = 40
    box_margin_left = margin // 2
    y = margin
    while y + box_w < height - margin:
        draw.rectangle([box_margin_left, y, box_margin_left + box_w, y + box_w], outline=(200,200,200), width=2)
        y += line_gap
    y = margin
    while y < height - margin:
        draw.line([(margin, y), (width - margin, y)], fill=(200, 220, 255), width=2)
        y += line_gap
    draw.text((width - 220, margin - 10), "No.", fill=(120,120,120))
    draw.text((width - 110, margin - 10), "Date", fill=(120,120,120))
    return img

def write_on_paper(base_img: Image.Image, text: str, x=120, y=70, max_width=None):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    if max_width is None:
        max_width = img.width - x - 80
    words = text.split()
    line = ""
    cur_y = y
    for w in words:
        test = (line + " " + w).strip()
        tw, th = draw.textsize(test, font=font)
        if tw > max_width:
            draw.text((x, cur_y), line, fill=(30,30,30), font=font)
            cur_y += th + 8
            line = w
        else:
            line = test
    if line:
        draw.text((x, cur_y), line, fill=(30,30,30), font=font)
    return img

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /write <text> to write on paper.")

async def write_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /write <text>")
        return
    text = " ".join(context.args)
    base = make_lined_paper()
    img = write_on_paper(base, text, x=120, y=90)
    bio = BytesIO()
    bio.name = "paper.jpg"
    img.save(bio, "JPEG")
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption=f"Written: {text}")

def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("write", write_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
