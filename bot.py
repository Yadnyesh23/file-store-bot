from pyrogram import Client, filters
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pyrogram.types import ReplyKeyboardMarkup  # Import for menu buttons

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

@app.on_message(filters.command("start"))
def start(client, message):
    if len(message.text.split()) > 1:  # Check if there's a parameter
        param = message.text.split()[1]
        if param.startswith("get_"):
            file_id = param.replace("get_", "")
            send_file(client, message, file_id)  # Call the function to send the file
        else:
            message.reply("❌ Invalid file link!")
    else:
        # Create a menu with buttons
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

@app.on_message(filters.command("stats"))
def stats(client, message):
    total_files = files_collection.count_documents({})
    user_files = files_collection.count_documents({"user_id": message.from_user.id})

    message.reply(
        f"📊 **File Storage Stats**\n"
        f"📂 Total Files Stored: `{total_files}`\n"
        f"👤 Your Uploaded Files: `{user_files}`"
    )

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
