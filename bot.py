import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ API Credentials
API_ID = 20969300
API_HASH = "2eecec277845829136373e481a575452"
BOT_TOKEN = "7292287878:AAHs52v0ff8aY7FKc5SiI7lTUxFmZnVQ_ys"

# ✅ Telegram Channel (Users Must Join Before Using Bot)
CHANNEL_USERNAME = "@BlackEagle_Sec"

# ✅ Initialize Bot
bot = Client("AITagBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# ✅ Global Stop Flag
stop_flag = False  

# ✅ Check if User is in Channel (Now Works for Public Channels!)
async def is_user_in_channel(user_id):
    try:
        user_channel_info = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return user_channel_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]
    except UserNotParticipant:
        return False
    except RPCError:
        return False  # If the bot cannot check, assume user is not in the channel

# ✅ Command: /start (With Join Button)
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    if not await is_user_in_channel(user_id):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔹 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]])
        await message.reply_text(f"🚨 **Join [our channel]({CHANNEL_USERNAME}) first to use this bot!**", disable_web_page_preview=True, reply_markup=keyboard)
        return

    welcome_text = (
        "✅ **Welcome BlackEagle Sec is here !**\n"
        "Use /run to tag members with random messages .\n"
        "Use /crun to tag all members with your custom message.\n"
        "Use /urun to tag a specific member repeatedly.\n"
        "Use /stop to stop any tagging process."
    )
    await message.reply_text(welcome_text)

# ✅ Command: /run (Tag All Members with Random Messages)
@bot.on_message(filters.command("run"))
async def tag_all(client, message):
    global stop_flag
    stop_flag = False  

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_user_in_channel(user_id):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔹 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]])
        await message.reply_text(f"🚨 **Join [our channel]({CHANNEL_USERNAME}) first to use this command!**", disable_web_page_preview=True, reply_markup=keyboard)
        return

    member = await client.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await message.reply_text("🚫 **Only admins can use this command!**")
        return

    await message.reply_text("✅ **Tagging all members...**")

    try:
        with open("word.txt", "r", encoding="utf-8") as file:
            words = file.readlines()
    except FileNotFoundError:
        await message.reply_text("⚠️ **word.txt file not found!**")
        return

    count = 0
    async for member in client.get_chat_members(chat_id):
        if stop_flag:  
            await message.reply_text("🛑 **Tagging Stopped!**")
            return

        if not member.user.is_bot:
            mention_text = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            random_message = f"**{random.choice(words).strip()}**"  
            try:
                await client.send_message(chat_id, f"{mention_text} {random_message}", disable_web_page_preview=True)
                count += 1
                await asyncio.sleep(2)  
            except FloodWait as e:
                await asyncio.sleep(e.value)

    await message.reply_text(f"✅ **Done! {count} members tagged.**")

# ✅ Command: /crun <message> (Tag All with Custom Message)
@bot.on_message(filters.command("crun"))
async def custom_tag(client, message):
    global stop_flag
    stop_flag = False  

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_user_in_channel(user_id):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔹 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]])
        await message.reply_text(f"🚨 **Join [our channel]({CHANNEL_USERNAME}) first to use this command!**", disable_web_page_preview=True, reply_markup=keyboard)
        return

    if len(message.command) < 2:
        await message.reply_text("⚠️ **Usage:** /crun <message>")
        return

    custom_message = " ".join(message.command[1:])
    await message.reply_text(f"✅ **Tagging all members with:**\n**{custom_message}**")

    count = 0
    async for member in client.get_chat_members(chat_id):
        if stop_flag:  
            await message.reply_text("🛑 **Tagging Stopped!**")
            return

        if not member.user.is_bot:
            mention_text = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            try:
                await client.send_message(chat_id, f"{mention_text} **{custom_message}**", disable_web_page_preview=True)
                count += 1
                await asyncio.sleep(2)
            except FloodWait as e:
                await asyncio.sleep(e.value)

    await message.reply_text(f"✅ **Done! {count} members tagged.**")

# ✅ Command: /urun <userid> <message> (Repeated Tagging)
@bot.on_message(filters.command("urun"))
async def user_repeat_tag(client, message):
    global stop_flag
    stop_flag = False  

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_user_in_channel(user_id):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔹 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]])
        await message.reply_text(f"🚨 **Join [our channel]({CHANNEL_USERNAME}) first to use this command!**", disable_web_page_preview=True, reply_markup=keyboard)
        return

    if len(message.command) < 3:
        await message.reply_text("⚠️ **Usage:** /urun <userid> <message>")
        return

    target_id = message.command[1]
    custom_message = " ".join(message.command[2:])

    try:
        target = await client.get_users(int(target_id))
        mention_text = f"[{target.first_name}](tg://user?id={target.id})"
    except:
        await message.reply_text("⚠️ **Invalid User ID!**")
        return

    await message.reply_text(f"✅ **Tagging {mention_text} repeatedly with:**\n**{custom_message}**")

    while not stop_flag:
        try:
            await client.send_message(chat_id, f"{mention_text} **{custom_message}**", disable_web_page_preview=True)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.value)

# ✅ Command: /stop (Stops Any Tagging)
@bot.on_message(filters.command("stop"))
async def stop_tagging(client, message):
    global stop_flag
    stop_flag = True  
    await message.reply_text("🛑 **Tagging Stopped!**")

# ✅ Auto-Restart on Internet Issues
def run_bot():
    while True:
        try:
            print("🤖 Bot Starting...")
            bot.run()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(4)  

# ✅ Start Bot
run_bot()
