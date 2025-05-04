# import streamlit as st
# from utils import extract_text_and_images, extract_clean_text, save_text, save_images
# from storage import save_page_to_db
# from start_mongo import start_mongodb_server, is_mongo_running
# from urllib.parse import urlparse
# import requests
# from bs4 import BeautifulSoup
# import os
# import subprocess
# import time
# from storage import get_recent_pages
# from io import BytesIO
#
# # === MongoDB Management ===
#
# # Track MongoDB process in Streamlit's session state
# #if "mongo_process" not in st.session_state:
# st.session_state.mongo_process = start_mongodb_server()
# time.sleep(10)
# # App UI
# st.title("🌐 Web Crawler App")
# st.write("Enter a URL to crawl and save data into MongoDB.")
# time.sleep(3)
# # Show MongoDB status
# if is_mongo_running():
#     st.success("✅ MongoDB is running")
# else:
#     st.error("❌ MongoDB is NOT running")
#
# # Button to stop MongoDB
# if st.button("🔴 Stop MongoDB Server"):
#     process = st.session_state.mongo_process
#     if process is not None:
#         process.terminate()
#         st.session_state.mongo_process = None
#         st.success("✅ MongoDB server terminated.")
#     else:
#         # Try to force-kill if Mongo started externally
#         try:
#             subprocess.run(["taskkill", "/F", "/IM", "mongod.exe"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             st.success("✅ MongoDB process killed manually.")
#         except subprocess.CalledProcessError:
#             st.warning("⚠️ Could not kill MongoDB. Maybe it's already off.")
#
# # === Crawler Form ===
# url = st.text_input("Enter URL (with https://)")
#
# if st.button("Start Crawling"):
#     if url:
#         progress = st.progress(0, text="Starting...")
#
#         try:
#             progress.progress(20, text="Fetching page...")
#             headers = {
#                 "User-Agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/122.0.0.0 Safari/537.36"
#                                 )
#                 }
#             response = requests.get(url, headers=headers)
#             soup = BeautifulSoup(response.text, "html.parser")
#             st.success(f"Page fetched: {url}")
#
#             progress.progress(60, text="Extracting and saving locally...")
#             folder_name = f"downloads/streamlit_page"
#             os.makedirs(folder_name, exist_ok=True)
#
#             clean_extracted_text = extract_clean_text(soup)
#             save_text(clean_extracted_text, folder_name)
#             save_images(soup, url, folder_name)
#
#             progress.progress(90, text="Saving to database...")
#             save_page_to_db(url, soup, clean_extracted_text)
#
#             progress.progress(100, text="Done! ✅")
#             st.success("Crawling and saving completed successfully!")
#             st.rerun()
#
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
#     else:
#         st.warning("Please enter a valid URL!")
# recent_pages = get_recent_pages()
#
# st.subheader("🕓 Recent Crawled Pages")
#
# recent_pages = get_recent_pages()
#
# if recent_pages:
#     for page in recent_pages:
#         st.markdown(f"**URL**: {page.get('url', 'N/A')}")
#         st.markdown(f"**Title**: {page.get('title', 'N/A')}")
#
#         with st.expander("🔍 View Full Text Snippet"):
#             st.write(page.get("text", "") or "No content extracted.")
#
#         images = page.get("images", [])[:8]  # show only first 8
#
#         if images:
#             st.markdown("📸 **Crawled Images:**")
#             cols = st.columns(len(images))
#             for i, img_url in enumerate(images):
#                 with cols[i]:
#                     try:
#                         # Fetch the image from the URL
#                         response = requests.get(img_url)
#                         if response.status_code == 200:
#                             # Convert to bytes and display without container_width param
#                             image_bytes = response.content
#                             st.image(image_bytes)  # Removed use_container_width parameter
#                         else:
#                             st.warning(f"Could not load image (HTTP {response.status_code})")
#                     except Exception as e:
#                         st.warning(f"Could not load image: {str(e)}")
#         else:
#             st.info("No images available.")
#         with st.expander("🧾 View Raw HTML"):
#             st.code(page.get("html", "No HTML saved"), language="html")
#
#         st.markdown("---")
# else:
#     st.info("No pages found in database yet.")


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
from io import BytesIO
import pandas as pd
from robot_parser import can_fetch  # Import the robots.txt parser
from crawler import crawl

# Set page configuration with dark theme
st.set_page_config(
    page_title="Web Crawler App",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark theme
st.markdown("""
<style>
    /* Base theme - dark */
    .stApp {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #BB86FC !important;
        margin-bottom: 1rem !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #BB86FC !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #3700B3;
        padding-bottom: 0.5rem;
    }

    /* URL display */
    .url-display {
        padding: 0.5rem;
        background-color: #2D2D2D;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #BB86FC;
        word-break: break-all;
    }

    /* Page title */
    .page-title {
        font-weight: 600;
        font-size: 1.2rem;
        color: #BB86FC;
    }

    /* Cards */
    .card {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #BB86FC;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Status indicators */
    .status-success {
        background-color: #1B5E20;
        color: #FFFFFF;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-error {
        background-color: #B71C1C;
        color: #FFFFFF;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-warning {
        background-color: #FF6D00;
        color: #FFFFFF;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Form styling */
    .crawler-form {
        background-color: #2D2D2D;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        border: 1px solid #3700B3;
    }

    /* Image containers */
    .image-container {
        border: 1px solid #424242;
        border-radius: 5px;
        padding: 0.5rem;
        background-color: #1E1E1E;
        margin-bottom: 0.5rem;
        height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .image-container img {
        max-height: 100%;
        object-fit: contain;
    }

    /* Text snippet */
    .text-snippet {
        max-height: 300px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #2D2D2D;
        border: 1px solid #424242;
        border-radius: 5px;
    }

    /* Expander headers */
    .expander-header {
        font-weight: 600;
        color: #BB86FC;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 4px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .stop-button button {
        background-color: #CF6679;
        color: black;
    }
    .stop-button button:hover {
        background-color: #B00020;
        color: white;
    }
    .crawl-button button {
        background-color: #03DAC6;
        color: black;
    }
    .crawl-button button:hover {
        background-color: #018786;
        color: white;
    }
    .start-button button {
        background-color: #BB86FC;
        color: black;
    }
    .start-button button:hover {
        background-color: #3700B3;
        color: white;
    }

    /* Fix tab styling for dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E1E1E;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2D2D2D;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #BB86FC;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3700B3 !important;
        color: white !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: #BB86FC;
    }

    /* Table styles */
    .dataframe {
        background-color: #2D2D2D !important;
    }
    .dataframe th {
        background-color: #3700B3 !important;
        color: white !important;
    }
    .dataframe td {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #3C3C3C;
    }

    /* Image grid styling */
    .image-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: flex-start;
    }
    .image-grid-item {
        flex: 0 0 calc(20% - 10px);
        max-width: calc(20% - 10px);
        box-sizing: border-box;
    }
    /* For mobile devices */
    @media (max-width: 768px) {
        .image-grid-item {
            flex: 0 0 calc(50% - 10px);
            max-width: calc(50% - 10px);
        }
    }

    /* Make content preview area nicer */
    .content-preview {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 1.5rem;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
        max-height: 300px;
        overflow-y: auto;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #2D2D2D;
    }
    ::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #888;
    }

    /* Robots.txt Status */
    .robots-allowed {
        background-color: #1B5E20;
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .robots-disallowed {
        background-color: #B71C1C;
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Create sidebar for MongoDB controls and settings
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #BB86FC;'>🕸️ Web Crawler</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Database Status")

    # MongoDB Status
    mongodb_status = st.empty()
    if is_mongo_running():
        mongodb_status.markdown("<div class='status-success'>✅ MongoDB is running</div>", unsafe_allow_html=True)
    else:
        mongodb_status.markdown("<div class='status-error'>❌ MongoDB is NOT running</div>", unsafe_allow_html=True)
        # Start MongoDB if needed
        st.markdown("<div class='start-button'>", unsafe_allow_html=True)
        if st.button("🚀 Start MongoDB Server"):
            st.session_state.mongo_process = start_mongodb_server()
            time.sleep(5)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Stop MongoDB button
    if is_mongo_running():
        with st.container():
            st.markdown("<div class='stop-button'>", unsafe_allow_html=True)
            if st.button("🔴 Stop MongoDB Server"):
                process = st.session_state.get("mongo_process")
                if process is not None:
                    process.terminate()
                    st.session_state.mongo_process = None
                else:
                    # Try to force-kill if Mongo started externally
                    try:
                        subprocess.run(["taskkill", "/F", "/IM", "mongod.exe"], check=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
                    except subprocess.CalledProcessError:
                        pass
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Crawler Settings
    st.markdown("### ⚙️ Crawler Settings")

    # User Agent
    user_agent = st.text_input(
        "User Agent",
        value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        help="Identifies your crawler to websites"
    )

    # Crawling Mode
    crawl_mode = st.radio(
        "Crawling Mode",
        ["Single Page", "Deep Crawl"],
        help="Single page: Crawl only the provided URL. Deep Crawl: Follow links on the same domain"
    )

    # Deep Crawl settings (only shown if Deep Crawl is selected)
    if crawl_mode == "Deep Crawl":
        max_pages = st.slider("Max Pages to Crawl", 1, 50, 5, help="Maximum number of pages to crawl")

    # Robots.txt Compliance
    respect_robots = st.checkbox("Respect robots.txt", value=True,
                                 help="Check and follow robots.txt rules (recommended)")

    st.markdown("---")
    st.markdown("### 📊 Stats")
    recent_pages = get_recent_pages()
    st.metric("Pages Crawled", len(recent_pages))

    # Get count of images
    image_count = sum(len(page.get("images", [])) for page in recent_pages)
    st.metric("Images Found", image_count)

# Main content
st.markdown("<h1 class='main-header'>🕸️ Web Crawler App</h1>", unsafe_allow_html=True)
st.markdown("Extract content and images from any website with just one click.")

# Crawler Form
st.markdown("<div class='crawler-form'>", unsafe_allow_html=True)
url = st.text_input("🔗 Enter URL to crawl (with https://)", placeholder="https://example.com")

# Robots.txt status checker (runs when URL is entered but before crawling)
if url and respect_robots:
    robots_status = st.empty()
    try:
        if can_fetch(url, user_agent):
            robots_status.markdown("<div class='robots-allowed'>✅ Allowed by robots.txt</div>", unsafe_allow_html=True)
        else:
            robots_status.markdown("<div class='robots-disallowed'>❌ Disallowed by robots.txt - Crawling blocked</div>",
                                   unsafe_allow_html=True)
    except Exception as e:
        robots_status.markdown(f"<div class='status-warning'>⚠️ Could not check robots.txt: {str(e)}</div>",
                               unsafe_allow_html=True)

cols = st.columns([3, 1])
with cols[0]:
    st.markdown("<div class='crawl-button'>", unsafe_allow_html=True)
    crawl_button = st.button("🚀 Start Crawling", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if crawl_button:
    if not url:
        st.warning("⚠️ Please enter a valid URL!")
    else:
        # Check robots.txt if respect_robots is True
        if respect_robots and not can_fetch(url, user_agent):
            st.error(
                "❌ This URL is disallowed by the site's robots.txt file. Crawling stopped to respect website policy.")
        else:
            # Create a nice progress display
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Check crawl mode
                    if crawl_mode == "Deep Crawl":
                        # Deep crawl with progress updates
                        status_text.markdown("🔄 **Starting deep crawl...**")
                        progress_bar.progress(10)

                        # Call the crawler with robots.txt compliance
                        crawl(url, max_pages=max_pages, user_agent=user_agent)

                        progress_bar.progress(100)
                        status_text.markdown(f"✅ **Deep crawl completed! Crawled up to {max_pages} pages.**")

                    else:
                        # Single page crawl
                        # Step 1: Fetching
                        status_text.markdown("🔄 **Fetching page content...**")
                        progress_bar.progress(20)

                        headers = {"User-Agent": user_agent}
                        response = requests.get(url, headers=headers)
                        soup = BeautifulSoup(response.text, "html.parser")

                        # Step 2: Processing
                        status_text.markdown("🔍 **Processing content...**")
                        progress_bar.progress(40)

                        folder_name = f"downloads/streamlit_page"
                        os.makedirs(folder_name, exist_ok=True)

                        # Step 3: Extracting
                        status_text.markdown("📄 **Extracting text...**")
                        progress_bar.progress(60)

                        clean_extracted_text = extract_clean_text(soup)
                        save_text(clean_extracted_text, folder_name)

                        # Step 4: Saving images
                        status_text.markdown("🖼️ **Saving images...**")
                        progress_bar.progress(80)

                        save_images(soup, url, folder_name)

                        # Step 5: Database
                        status_text.markdown("💾 **Saving to database...**")
                        progress_bar.progress(90)

                        save_page_to_db(url, soup, clean_extracted_text)

                        # Complete
                        progress_bar.progress(100)
                        status_text.markdown("✅ **Crawling complete!**")

                    time.sleep(1)
                    # Show success message
                    st.success("Crawling and saving completed successfully!")
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error: {str(e)}")

# Recent Pages Section
st.markdown("<h2 class='sub-header'>📚 Recent Crawled Pages</h2>", unsafe_allow_html=True)

recent_pages = get_recent_pages()

if recent_pages:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📑 Card View", "📊 Table View"])

    with tab1:
        # Card view
        for page in recent_pages:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                # Website info
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"<div class='page-title'>{page.get('title', 'No Title')}</div>",
                                unsafe_allow_html=True)
                    st.markdown(f"<div class='url-display'>{page.get('url', 'N/A')}</div>", unsafe_allow_html=True)
                with col2:
                    crawl_time = page.get('created_at', 'Unknown')
                    if crawl_time != 'Unknown':
                        crawl_time = crawl_time.strftime("%Y-%m-%d %H:%M")
                    st.markdown(f"**Crawled:** {crawl_time}")

                # Content preview
                with st.expander("📝 Content Preview"):
                    st.markdown("<div class='content-preview'>", unsafe_allow_html=True)
                    text_preview = page.get("text", "")
                    if text_preview:
                        # Limit preview
                        if len(text_preview) > 500:
                            text_preview = text_preview[:500] + "..."
                        st.markdown(text_preview)
                    else:
                        st.info("No content extracted.")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Images
                images = page.get("images", [])
                if images:
                    st.markdown("### 🖼️ Images")

                    # Display up to 5 images
                    img_cols = st.columns(min(5, len(images[:5])))
                    for i, img_url in enumerate(images[:5]):  # Show first 5
                        with img_cols[i % len(img_cols)]:
                            try:
                                # Fetch image with timeout and error handling
                                try:
                                    response = requests.get(img_url, timeout=5)
                                    if response.status_code == 200:
                                        # Try to determine content type
                                        content_type = response.headers.get('Content-Type', '')
                                        if 'image' in content_type:
                                            st.image(response.content, caption=f"Image {i + 1}", use_column_width=True)
                                        else:
                                            st.warning(f"Not an image (type: {content_type})")
                                    else:
                                        st.warning(f"HTTP {response.status_code}")
                                except requests.exceptions.RequestException as e:
                                    st.warning(f"Request error: {e.__class__.__name__}")
                            except Exception as e:
                                st.warning(f"Error: {str(e)[:50]}")

                    if len(images) > 5:
                        st.info(f"+ {len(images) - 5} more images")
                else:
                    st.info("No images found.")

                # Raw HTML option
                with st.expander("🧾 View Raw HTML"):
                    st.code(page.get("html", "No HTML saved")[:5000] + "..." if len(
                        page.get("html", "")) > 5000 else page.get("html", "No HTML saved"), language="html")

                st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        # Create a table view of the data
        table_data = []
        for page in recent_pages:
            crawl_time = page.get('created_at', 'Unknown')
            if crawl_time != 'Unknown':
                crawl_time = crawl_time.strftime("%Y-%m-%d %H:%M")

            table_data.append({
                "Title": page.get('title', 'No Title')[:50] + "..." if len(
                    page.get('title', 'No Title')) > 50 else page.get('title', 'No Title'),
                "URL": page.get('url', 'N/A'),
                "Crawled At": crawl_time,
                "Images": len(page.get('images', [])),
                "Content Length": len(page.get('text', ''))
            })

        # Display as a dataframe
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

else:
    st.info("🔍 No pages found in database yet. Start crawling to see results!")

# Add footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; padding: 1rem;'>"
    "Web Crawler App v1.0 | Respects robots.txt"
    "</div>",
    unsafe_allow_html=True
)