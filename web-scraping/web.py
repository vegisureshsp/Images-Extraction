from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
import time
from urllib.parse import urljoin, urlparse

# List of websites to scrape
websites = [
    "https://icic.org/","https://www.whizlabs.com/"  # Change this to your target website
]

# Selenium Setup
options = Options()
options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def clean_filename(url):
    """Generate a clean folder name from URL"""
    return url.replace("https://", "").replace("http://", "").replace("/", "_")

def download_image(image_url, folder):
    """Download and save image"""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            filename = os.path.join(folder, image_url.split("/")[-1].split("?")[0])
            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"📸 Downloaded: {filename}")
    except Exception as e:
        print(f"⚠️ Failed to download {image_url}: {e}")

def get_internal_links(soup, base_url):
    """Find all internal links on a page"""
    domain = urlparse(base_url).netloc
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == domain:  # Ensure it's an internal link
            links.add(full_url)

    return list(links)

def scrape_page(url, base_folder):
    """Scrape a single page for text, images, and tables"""
    print(f"🔍 Scraping: {url}")

    # Create folders
    page_folder = os.path.join(base_folder, clean_filename(url))
    TEXT_FOLDER = os.path.join(page_folder, "text")
    IMAGE_FOLDER = os.path.join(page_folder, "images")
    os.makedirs(TEXT_FOLDER, exist_ok=True)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    # Open website
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # -------------------- Extract Text --------------------
    text_content = []

    for tag in ["h1", "h2", "h3", "p"]:
        for element in soup.find_all(tag):
            text_content.append(element.text.strip())

    with open(os.path.join(TEXT_FOLDER, "scraped_text.txt"), "w", encoding="utf-8") as file:
        file.write("\n".join(text_content))

    print("✅ Text saved!")

    # -------------------- Extract Images --------------------
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url:
            img_url = urljoin(url, img_url)
            download_image(img_url, IMAGE_FOLDER)

    print("✅ Images saved!")

    # -------------------- Extract Tables --------------------
    # -------------------- Extract Tables --------------------
    tables = soup.find_all("table")

    if tables:
        for index, table in enumerate(tables):
            rows = []
            headers = [th.text.strip() for th in table.find_all("th")]

            for row in table.find_all("tr"):
                cells = [td.text.strip() for td in row.find_all("td")]
                if cells:
                    rows.append(cells)

        # Handle cases where the number of columns is inconsistent
            max_cols = max(len(row) for row in rows) if rows else 0
            if headers and len(headers) != max_cols:
                headers = None  # Ignore headers if they don't match the data

            df = pd.DataFrame(rows, columns=headers if headers else None)
            df.to_csv(os.path.join(TEXT_FOLDER, f"scraped_table_{index+1}.csv"), index=False, encoding="utf-8")

        print("✅ Tables saved!")
    else:
        print("⚠️ No tables found!")


    return get_internal_links(soup, url)

for website_url in websites:
    print(f"\n🌍 Scraping website: {website_url}")

    # Create base folder
    site_folder = os.path.join("scraped_data", clean_filename(website_url))
    os.makedirs(site_folder, exist_ok=True)

    # Start with the homepage
    pages_to_scrape = [website_url]
    scraped_pages = set()

    while pages_to_scrape:
        current_page = pages_to_scrape.pop(0)
        if current_page not in scraped_pages:
            internal_links = scrape_page(current_page, site_folder)
            scraped_pages.add(current_page)

            # Add new internal links to scrape
            for link in internal_links:
                if link not in scraped_pages:
                    pages_to_scrape.append(link)

print("\n🎉 Scraping completed for all websites!")
driver.quit()
