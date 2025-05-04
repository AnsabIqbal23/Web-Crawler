# from utils import extract_text_and_images
# from urllib.parse import urljoin, urlparse
# from collections import deque
# import requests
# from bs4 import BeautifulSoup
#
# def crawl(start_url, max_pages=1):
#     visited = set()
#     queue = deque([start_url])
#     count = 0
#
#     while queue and count < max_pages:
#         current_url = queue.popleft()
#         if current_url in visited:
#             continue
#
#         print(f"Crawling: {current_url}")
#         visited.add(current_url)
#         extract_text_and_images(current_url, folder=f"downloads/page_{count}")
#         count += 1
#
#         try:
#             response = requests.get(current_url)
#             soup = BeautifulSoup(response.text, "html.parser")
#
#             for link in soup.find_all('a', href=True):
#                 href = link['href']
#                 full_url = urljoin(current_url, href)
#                 if urlparse(full_url).netloc == urlparse(start_url).netloc:
#                     queue.append(full_url)
#         except Exception as e:
#             print(f"Error crawling {current_url}: {e}")
#
# if __name__ == "__main__":
#     seed_url = "https://medium.com"
#     crawl(seed_url, max_pages=1)


from utils import extract_text_and_images
from urllib.parse import urljoin, urlparse
from collections import deque
import requests
from bs4 import BeautifulSoup
from robot_parser import can_fetch


def crawl(start_url, max_pages=1, user_agent="WebCrawlerBot"):
    visited = set()
    queue = deque([start_url])
    count = 0

    while queue and count < max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        # Check robots.txt rules before crawling
        if not can_fetch(current_url, user_agent):
            print(f"Skipping {current_url} - disallowed by robots.txt")
            continue

        print(f"Crawling: {current_url}")
        visited.add(current_url)
        result = extract_text_and_images(current_url, folder=f"downloads/page_{count}")

        # Only increment counter if we successfully processed the page
        if result:
            count += 1

        try:
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)

                # Only queue URLs on the same domain
                if urlparse(full_url).netloc == urlparse(start_url).netloc:
                    # Check robots.txt before adding to queue
                    if can_fetch(full_url, user_agent) and full_url not in visited:
                        queue.append(full_url)

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")


if __name__ == "__main__":
    seed_url = "https://medium.com"
    crawl(seed_url, max_pages=1)