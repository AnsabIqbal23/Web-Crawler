from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    print("✅ MongoDB is accepting connections on port 27017.")
except ConnectionFailure as e:
    print(f"❌ Connection failed: {e}")
