from pyrogram import Client, filters
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pyrogram.types import ReplyKeyboardMarkup  # For menu buttons

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

app = Client("file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

client = MongoClient(MONGO_URI)
db = client['file_store']
files_collection = db['files']
BOT_USERNAME = "file_23_bot"  # Replace with your bot's username

# Function to show main menu
def show_main_menu(message):
    keyboard = ReplyKeyboardMarkup(
        [["📤 Upload File", "📂 My Files"], ["📊 Stats", "ℹ️ Help"]],
        resize_keyboard=True
    )

    message.reply(
        "📁 **Welcome to File Store Bot!**\n"
        "Send any file, and I'll store it for you.\n\n"
        "**Available Commands:**\n"
        "📤 Upload File - Send a file to store\n"
        "📂 My Files - View your stored files\n"
        "📊 Stats - See file storage stats\n"
        "ℹ️ Help - Get bot usage instructions",
        reply_markup=keyboard
    )

@app.on_message(filters.command("start"))
def start(client, message):
    show_main_menu(message)

@app.on_message(filters.command("stats") | filters.regex("^📊 Stats$"))
def stats(client, message):
    total_files = files_collection.count_documents({})
    user_files = files_collection.count_documents({"user_id": message.from_user.id})

    message.reply(
        f"📊 **File Storage Stats**\n"
        f"📂 Total Files Stored: `{total_files}`\n"
        f"👤 Your Uploaded Files: `{user_files}`"
    )

@app.on_message(filters.regex("^📂 My Files$"))
def my_files(client, message):
    user_id = message.from_user.id
    user_files = list(files_collection.find({"user_id": user_id}))

    if not user_files:
        message.reply("📂 You have no stored files.")
        return

    reply_text = "📂 **Your Stored Files:**\n\n"
    for file in user_files[:10]:  # Limit to 10 for now
        file_link = f"https://t.me/{BOT_USERNAME}?start=get_{file['_id']}"
        reply_text += f"🔹 [{file['file_name']}]({file_link})\n"

    message.reply(reply_text, disable_web_page_preview=True)

@app.on_message(filters.regex("^ℹ️ Help$"))
def help_command(client, message):
    message.reply(
        "ℹ️ **How to Use This Bot:**\n"
        "📤 Send any **document, video, photo, or audio**, and I'll store it.\n"
        "📂 Click **My Files** to see your stored files.\n"
        "📊 Click **Stats** to check how many files are saved.\n"
        "🔗 I'll provide you with a **retrieval link** for each file!"
    )

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
