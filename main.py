from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import base64
from urllib.parse import urljoin
import time

SAVE_FOLDER = "downloaded_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-blink-features=AutomationControlled")  # Reduce bot detection
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

websites = ["https://website.rbi.org.in"]

def save_base64_image(base64_data, filename):
    """Save Base64 image to file."""
    try:
        image_data = base64.b64decode(base64_data.split(",")[1])  # Remove prefix (data:image/png;base64,)
        file_path = os.path.join(SAVE_FOLDER, filename)
        with open(file_path, "wb") as file:
            file.write(image_data)
        print(f"Saved Base64 Image: {file_path}")
    except Exception as e:
        print(f"Failed to save Base64 image: {e}")

def download_image(image_url):
    """Download and save image from URL."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            filename = os.path.join(SAVE_FOLDER, image_url.split("/")[-1].split("?")[0])  # Remove URL parameters
            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")

for website in websites:
    print(f"Extracting images from {website}...")
    driver.get(website)
    time.sleep(5)  # Wait for the page to fully load

    images = driver.find_elements("tag name", "img")

    for index in range(len(images)):
        try:
            images = driver.find_elements("tag name", "img")  # Re-fetch elements to avoid stale references
            img = images[index]
            img_url = img.get_attribute("src")

            if img_url:
                if img_url.startswith("data:image"):  # Handle Base64 images
                    save_base64_image(img_url, f"base64_image_{index}.png")
                else:
                    img_url = urljoin(website, img_url)  # Convert relative to absolute URL
                    print(f"Found Image: {img_url}")
                    download_image(img_url)
        except Exception as e:
            print(f"Error processing image {index}: {e}")

driver.quit()
print("Image extraction completed!")
