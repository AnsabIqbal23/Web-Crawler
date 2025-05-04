import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from storage import save_page_to_db

def clean_text(raw_text):
    cleaned = re.sub(r'\s+', ' ', raw_text)
    cleaned = re.sub(r'[^A-Za-z0-9,.!?\'" ]+', '', cleaned)
    return cleaned.strip()

def save_text(text, folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "content.txt"), "w", encoding="utf-8") as f:
        f.write(text)

def save_images(soup, base_url, folder):
    img_folder = os.path.join(folder, "images")
    os.makedirs(img_folder, exist_ok=True)
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            img_url = urljoin(base_url, src)
            try:
                img_data = requests.get(img_url).content
                img_name = os.path.basename(src.split("?")[0])
                with open(os.path.join(img_folder, img_name), "wb") as img_file:
                    img_file.write(img_data)
            except Exception as e:
                print(f"Failed to download image {img_url}: {e}")

def extract_clean_text(soup):
    extracted = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        if tag.name.startswith('h'):
            extracted.append("\n\n# " + tag.get_text(separator=" ", strip=True))  # Add space between inner texts
        elif tag.name == 'p':
            extracted.append("\n" + tag.get_text(separator=" ", strip=True))
        elif tag.name == 'li':
            extracted.append(" - " + tag.get_text(separator=" ", strip=True))
    return "\n".join(extracted)

def extract_text_and_images(url, folder="downloads"):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "page.html"), "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        clean_extracted_text = extract_clean_text(soup)
        save_text(clean_extracted_text, folder)
        save_images(soup, url, folder)

        # Save into MongoDB
        save_page_to_db(url, soup, clean_extracted_text)

    except Exception as e:
        print(f"Error extracting from {url}: {e}")
