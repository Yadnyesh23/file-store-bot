from pyrogram import Client, filters
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

app = Client("file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

client = MongoClient(MONGO_URI)
db = client['file_store']
files_collection = db['files']

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("📁 Welcome! Send any file, and I'll store it for you.")

@app.on_message(filters.document | filters.video | filters.photo | filters.audio)
def save_file(client, message):
    user_id = message.from_user.id
    file_id = message.document.file_id if message.document else message.video.file_id if message.video else message.photo.file_id if message.photo else message.audio.file_id
    file_name = message.document.file_name if message.document else "file"

    file_data = {"user_id": user_id, "file_id": file_id, "file_name": file_name}
    file_entry = files_collection.insert_one(file_data)

    message.reply_text(f"✅ File stored!\nID: `{file_entry.inserted_id}`\nUse /getfile {file_entry.inserted_id} to retrieve it.")

@app.on_message(filters.command("getfile"))
def get_file(client, message):
    msg_parts = message.text.split(" ", 1)
    if len(msg_parts) < 2:
        message.reply_text("Usage: /getfile <file_id>")
        return

    file_id = msg_parts[1]
    file_entry = files_collection.find_one({"_id": file_id})

    if file_entry:
        client.send_document(chat_id=message.chat.id, document=file_entry["file_id"], caption=f"📁 {file_entry['file_name']}")
    else:
        message.reply_text("❌ File not found!")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
