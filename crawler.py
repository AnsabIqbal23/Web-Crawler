from utils import extract_text_and_images
from urllib.parse import urljoin, urlparse
from collections import deque
import requests
from bs4 import BeautifulSoup

def crawl(start_url, max_pages=1):
    visited = set()
    queue = deque([start_url])
    count = 0

    while queue and count < max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")
        visited.add(current_url)
        extract_text_and_images(current_url, folder=f"downloads/page_{count}")
        count += 1

        try:
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                if urlparse(full_url).netloc == urlparse(start_url).netloc:
                    queue.append(full_url)
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")

if __name__ == "__main__":
    seed_url = "https://medium.com"
    crawl(seed_url, max_pages=1)
