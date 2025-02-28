from pyrogram import Client, filters
import os
from pymongo import MongoClient
from bson import ObjectId
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
        message.reply("📁 Welcome! Send any file, and I'll store it for you.")

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

    file_data = {"user_id": user_id, "file_id": file_id, "file_name": file_name}
    file_entry = files_collection.insert_one(file_data)

    file_link = f"https://t.me/{BOT_USERNAME}?start=get_{file_entry.inserted_id}"
    
    files_collection.update_one({"_id": file_entry.inserted_id}, {"$set": {"file_link": file_link}})

    message.reply(f"✅ File stored!\nClick below to retrieve it:\n🔗 [Get File]({file_link})", disable_web_page_preview=True)

def send_file(client, message, file_id):
    try:
        file_entry = files_collection.find_one({"_id": ObjectId(file_id)})
    except Exception:
        message.reply("❌ Invalid or expired file link!")
        return

    if file_entry:
        client.send_document(chat_id=message.chat.id, document=file_entry["file_id"], caption=f"📁 {file_entry['file_name']}")
    else:
        message.reply("❌ File not found!")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
