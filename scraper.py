import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from deep_translator import GoogleTranslator
from collections import Counter
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json

# BrowserStack credentials
user_name = "<hirkanikashid_lt3Mcy>"  # Replace with your BrowserStack username
access_key = "<vsjHRbAGz5Kiqra8dNkh>"  # Replace with your BrowserStack access key

# Setup for BrowserStack using options
options = Options()

# Setting up desired capabilities for BrowserStack
capabilities = {
    'browserName': 'Chrome',
    'browserVersion': 'latest',
    'os': 'Windows',
    'osVersion': '11',
    'name': 'Selenium Web Scraping Test',  # Test name
    'build': 'bs-web-scraping-build',  # Build name
    'project': 'Web Scraping Project',  # Project name
    'browserstack.local': 'true',  # Local testing
    'debug': 'true',  # Enable debug logs
    'networkLogs': 'true',  # Enable network logs
    'consoleLogs': 'info',  # Enable console logs for debugging
}

# Use the options object to set the capabilities
options.add_experimental_option('prefs', capabilities)

# Remote WebDriver setup for BrowserStack
driver = webdriver.Remote(
    command_executor=f'https://{user_name}:{access_key}@hub-cloud.browserstack.com/wd/hub',
    options=options
)

# Define URL
url = "https://elpais.com/opinion/"
driver.get(url)
time.sleep(3)  # Allow page to load

# Translator
translator = GoogleTranslator(source="es", target="en")

# Create folder for images
if not os.path.exists("images"):
    os.makedirs("images")

# Store results
article_data = []
all_words = []

# Get first 5 article links
article_links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, "h2 a")[:5]]

for index, article_url in enumerate(article_links):
    driver.get(article_url)
    time.sleep(3)  # Allow article page to load

    try:
        # Get article title
        article_title = driver.find_element(By.TAG_NAME, "h1").text
    except:
        print(f"Failed to fetch title for article {index + 1}")
        continue

    # Get article content (first 5 paragraphs)
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    article_content = "\n".join([p.text for p in paragraphs[:5]])

    # Translate title
    translated_title = translator.translate(article_title)

    # Store words for frequency analysis
    all_words.extend([word.strip(".,'\"!?") for word in translated_title.lower().split()])

    # Download image if available
    try:
        img_element = driver.find_element(By.TAG_NAME, "img")
        img_url = img_element.get_attribute("src")

        if img_url and not img_url.endswith(".svg"):  # Skip SVG images
            img_data = requests.get(img_url).content
            img_filename = f"images/article_{index + 1}.jpg"
            with open(img_filename, "wb") as img_file:
                img_file.write(img_data)
            print(f"Image saved: {img_filename}")
        else:
            print("No suitable image found.")
    except:
        print("No image found.")

    # Store data
    article_data.append((article_title, translated_title, article_content))
    print(f"\nOriginal: {article_title}\nTranslated: {translated_title}\n")

# Close browser
driver.quit()

# Find most repeated words
word_counts = Counter(all_words)
common_words = {word: count for word, count in word_counts.items() if count > 1}

# Print common words
print("\nRepeated Words Analysis:")
for word, count in common_words.items():
    print(f"{word}: {count} times")
