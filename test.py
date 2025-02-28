from pymongo import MongoClient

MONGO_URI = "mongodb+srv://yadnyesh23:yadnyesh%402316@cluster0.ftvbq.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    client.server_info()  # Forces a connection check
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
