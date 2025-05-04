import streamlit as st
from utils import extract_text_and_images, extract_clean_text, save_text, save_images
from storage import save_page_to_db
from start_mongo import start_mongodb_server, is_mongo_running
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os
import subprocess
import time
from storage import get_recent_pages

# === MongoDB Management ===

# Track MongoDB process in Streamlit's session state
#if "mongo_process" not in st.session_state:
st.session_state.mongo_process = start_mongodb_server()
time.sleep(10)
# App UI
st.title("🌐 Web Crawler App")
st.write("Enter a URL to crawl and save data into MongoDB.")
time.sleep(3)
# Show MongoDB status
if is_mongo_running():
    st.success("✅ MongoDB is running")
else:
    st.error("❌ MongoDB is NOT running")

# Button to stop MongoDB
if st.button("🔴 Stop MongoDB Server"):
    process = st.session_state.mongo_process
    if process is not None:
        process.terminate()
        st.session_state.mongo_process = None
        st.success("✅ MongoDB server terminated.")
    else:
        # Try to force-kill if Mongo started externally
        try:
            subprocess.run(["taskkill", "/F", "/IM", "mongod.exe"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            st.success("✅ MongoDB process killed manually.")
        except subprocess.CalledProcessError:
            st.warning("⚠️ Could not kill MongoDB. Maybe it’s already off.")

# === Crawler Form ===
url = st.text_input("Enter URL (with https://)")

if st.button("Start Crawling"):
    if url:
        progress = st.progress(0, text="Starting...")

        try:
            progress.progress(20, text="Fetching page...")
            headers = {
                "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
                                )
                }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            st.success(f"Page fetched: {url}")

            progress.progress(60, text="Extracting and saving locally...")
            folder_name = f"downloads/streamlit_page"
            os.makedirs(folder_name, exist_ok=True)

            clean_extracted_text = extract_clean_text(soup)
            save_text(clean_extracted_text, folder_name)
            save_images(soup, url, folder_name)

            progress.progress(90, text="Saving to database...")
            save_page_to_db(url, soup, clean_extracted_text)

            progress.progress(100, text="Done! ✅")
            st.success("Crawling and saving completed successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid URL!")
recent_pages = get_recent_pages()

st.subheader("🕓 Recent Crawled Pages")

recent_pages = get_recent_pages()

if recent_pages:
    for page in recent_pages:
        st.markdown(f"**URL**: {page.get('url', 'N/A')}")
        st.markdown(f"**Title**: {page.get('title', 'N/A')}")

        with st.expander("🔍 View Full Text Snippet"):
            st.write(page.get("text", "") or "No content extracted.")

        images = page.get("images", [])[:2]  # show only first 2

        if images:
            st.markdown("📸 **Crawled Images:**")
            cols = st.columns(len(images))
            for i, img_path in enumerate(images):
                with cols[i]:
                    try:
                        st.image(img_path, use_container_width=True)
                    except:
                        st.warning("Could not load image.")
        else:
            st.info("No images available.")
        with st.expander("🧾 View Raw HTML"):
            st.code(page.get("html", "No HTML saved"), language="html")    

        st.markdown("---")
else:
    st.info("No pages found in database yet.")
