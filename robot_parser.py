from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def can_fetch(url, user_agent="WebCrawlerBot"):
    """
    Check if the URL can be fetched according to the site's robots.txt rules

    Args:
        url (str): The URL to check
        user_agent (str): The user agent string to identify your crawler

    Returns:
        bool: True if the URL can be fetched, False otherwise
    """
    try:
        # Parse the URL to get the base domain
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Initialize the RobotFileParser
        rp = RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")

        # Read and parse the robots.txt file
        rp.read()

        # Check if our bot can fetch the URL
        return rp.can_fetch(user_agent, url)

    except Exception as e:
        # If there's an error (like no robots.txt), log it and return True
        print(f"Error checking robots.txt for {url}: {e}")
        return True  # Default to True if robots.txt cannot be parsed
