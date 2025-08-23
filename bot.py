from pyrogram import Client
import asyncio
import os

API_ID = 21081718
API_HASH = "fec3c59a0f36beb71199dba4459eef86"
SESSION = "BQFBrnYAl-pWnXbngB408FvSpoCaD7zojyTEPq9HUho4f_6juAcAzJ7TuF0v2TCZ0ahvEsEHjHhxWxyq9VbYwCh1mfUQvtHiy6WLaSor8F0g_jaz07f-W8_Gy6NQLiEJt_YXrhy4Py0L6MnTSxb4U_Xn4PWlQQ934BD-nh8BxyCgTV_DcQrvA8YwpWDGeKem1ZaAK8lQvtcCj5jmNs4WBHNSXchphObU_MxfZm_-lKCABX3CYY_I_CIyNMQH9WUIp2syavT-9iakCWa8WtMN-NFrxPc6LX14KxveI24ZmGeBj2_bwxWTDrzrJj4ppYiGZ6Xvo06tAlKkmFY4bihnqvTPgbopYAAAAAGxU39QAA"
BOT_USERNAME = "@DemoEscrowerBot"  # bot username fill

app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)

async def create_escrow():
    # Supergroup banao
    new_chat = await app.create_supergroup("Escrow Group", "Automatic escrow group bana diya gaya")
    
    # Bot ko group me add karo
    await app.add_chat_members(new_chat.id, [BOT_USERNAME])
    
    # Invite link nikalo
    link = await app.export_chat_invite_link(new_chat.id)
    
    # Link ko file me save karo
    with open("escrow_link.txt", "w") as f:
        f.write(link)
    
    print("✅ Group created:", link)

@app.on_message()
async def handle_msg(client, message):
    if message.text == "CREATE_ESCROW":
        await create_escrow()

app.run()
