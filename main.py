from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
from urllib.parse import urljoin

SAVE_FOLDER = "downloaded_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

options = Options()
options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

websites = ["https://eficens.com", "https://icic.org"]

def download_image(image_url):
    """Download and save image."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            filename = os.path.join(SAVE_FOLDER, image_url.split("/")[-1])
            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")

for website in websites:
    print(f"Extracting images from {website}...")
    driver.get(website)
    
    images = driver.find_elements("tag name", "img")
    
    for img in images:
        img_url = img.get_attribute("src")
        if img_url:
            img_url = urljoin(website, img_url)
            print(f"Found Image: {img_url}")
            download_image(img_url)

driver.quit()
print("Image extraction completed!")
