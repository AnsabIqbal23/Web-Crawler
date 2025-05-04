from pymongo import MongoClient
from urllib.parse import urljoin
from pymongo.errors import ConnectionFailure
from datetime import datetime

# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")

# Access the database and collection
db = client.webcrawler_db
collection = db.pages

def save_page_to_db(url, soup, clean_text):
    try:
        # Prepare page data with HTML and timestamp
        page_data = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "No Title",
            "text": clean_text,
            "html": str(soup),  # ✅ Save raw HTML
            "images": [
                urljoin(url, img['src'])
                for img in soup.find_all('img')
                    if img.get('src') and not img['src'].startswith("data:")],
            "created_at": datetime.utcnow()
        }

        collection.insert_one(page_data)
        print(f"✅ Saved {url} to database.")

    except Exception as e:
        print(f"❌ Error saving {url} to database: {e}")

def get_recent_pages(limit=5):
    try:
        return list(collection.find().sort("_id", -1).limit(limit))
    except ConnectionFailure:
        return []
