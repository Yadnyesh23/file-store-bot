from pyrogram import Client, filters
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pyrogram.types import ReplyKeyboardMarkup

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Initialize Pyrogram bot
app = Client("file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['file_store']
files_collection = db['files']
BOT_USERNAME = "file_23_bot"  # Replace with your bot's username

# Function to show main menu
def show_main_menu(message):
    keyboard = ReplyKeyboardMarkup(
        [["📤 Gen Link", "📂 My Files"], ["📊 Stats", "ℹ️ Help"]],
        resize_keyboard=True
    )
    message.reply(
        "📁 **Welcome to File Store Bot!**\n"
        "Send any file, and I'll store it for you.\n\n"
        "**Available Commands:**\n"
        "📤 Gen Link - Generate a file link\n"
        "📂 My Files - View your stored files\n"
        "📊 Stats - Check total stored files\n"
        "ℹ️ Help - Get bot usage instructions",
        reply_markup=keyboard
    )

# Start command
@app.on_message(filters.command("start"))
def start(client, message):
    show_main_menu(message)

# Stats command
@app.on_message(filters.command("stats") | filters.regex("^📊 Stats$"))
def stats(client, message):
    total_files = files_collection.count_documents({})
    user_files = files_collection.count_documents({"user_id": message.from_user.id})

    message.reply(
        f"📊 **File Storage Stats**\n"
        f"📂 Total Files Stored: `{total_files}`\n"
        f"👤 Your Uploaded Files: `{user_files}`"
    )

# Help command
@app.on_message(filters.command("help") | filters.regex("^ℹ️ Help$"))
def help_command(client, message):
    message.reply(
        "ℹ️ **How to Use This Bot:**\n"
        "✅ **Send a file** (document, video, photo, audio) and I'll store it.\n"
        "🔗 Use **Gen Link** to get a retrieval link.\n"
        "📂 Click **My Files** to see all your stored files.\n"
        "📊 Click **Stats** to see total file count.\n"
        "🚀 **Retrieve any file by clicking its link!**"
    )

# Store files automatically
@app.on_message(filters.document | filters.video | filters.photo | filters.audio)
def save_file(client, message):
    user_id = message.from_user.id
    file_id = (
        message.document.file_id if message.document else
        message.video.file_id if message.video else
        message.photo.file_id if message.photo else
        message.audio.file_id
    )
    file_name = message.document.file_name if message.document else "file"

    # Save file data in MongoDB
    file_data = {"user_id": user_id, "file_id": file_id, "file_name": file_name}
    file_entry = files_collection.insert_one(file_data)

    file_link = f"https://t.me/{BOT_USERNAME}?start=get_{file_entry.inserted_id}"
    files_collection.update_one({"_id": file_entry.inserted_id}, {"$set": {"file_link": file_link}})

    message.reply(f"✅ File stored!\nClick below to retrieve it:\n [Get File]({file_link})", disable_web_page_preview=True)

# Generate link command
@app.on_message(filters.command("genlink") | filters.regex("^📤 Gen Link$"))
def gen_link(client, message):
    user_id = message.from_user.id
    user_files = list(files_collection.find({"user_id": user_id}))

    if not user_files:
        message.reply("📂 You have no stored files. Send a file first!")
        return

    reply_text = "📂 **Your Stored Files:**\n\n"
    for file in user_files[:10]:  # Limit to 10 for now
        file_link = f"https://t.me/{BOT_USERNAME}?start=get_{file['_id']}"
        reply_text += f"🔹 [{file['file_name']}]({file_link})\n"

    message.reply(reply_text, disable_web_page_preview=True)

# Retrieve files via start command
