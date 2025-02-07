import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import pickle
import random
import os
import logging
from datetime import datetime

# Setup Logging
log_file = "../logs/scraper.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to extract structured details (beds, baths, sqft)
def extract_details(detail_text):
    beds_pattern = re.search(r"(\d+)\s*bds?", detail_text)
    baths_pattern = re.search(r"(\d+)\s*ba", detail_text)
    sqft_pattern = re.search(r"([\d,]+)\s*sqft", detail_text)

    return {
        "bedrooms": beds_pattern.group(1) if beds_pattern else "N/A",
        "bathrooms": baths_pattern.group(1) if baths_pattern else "N/A",
        "square_feet": sqft_pattern.group(1) if sqft_pattern else "N/A",
    }

# Function to Load Cookies (Avoid CAPTCHA)
def load_cookies(driver, cookie_file="../data/zillow_cookies.pkl"):
    if os.path.exists(cookie_file):
        cookies = pickle.load(open(cookie_file, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("✅ Cookies loaded successfully.")
    else:
        logging.warning("⚠️ No cookies found. Run `save_cookies.py` first!")

# Function to Scroll Until No More Listings Load
def scroll_and_load(driver, max_scrolls=30):
    logging.info("🔄 Starting deep scrolling to load all listings...")

    last_count = 0
    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 5)) 

        elements = driver.find_elements(By.XPATH, "//article")
        new_count = len(elements)

        if new_count == last_count:
            logging.info(f"✅ No more new listings after {new_count} results.")
            break

        logging.info(f"🔄 Scroll {i+1}: Loaded {new_count} listings.")
        last_count = new_count

    logging.info(f"✅ Scrolling complete. Total listings loaded: {last_count}")

# Function to Click "Next Page" Until No More Pages
def click_next_page(driver):
    try:
        next_button = driver.find_element(By.XPATH, "//a[@title='Next page']")
        next_button.click()
        time.sleep(random.uniform(3, 6))
        logging.info("✅ Clicked 'Next Page'.")
        return True
    except:
        logging.info("✅ No more pages found.")
        return False

# Function to save data to CSV
def save_data_to_csv(data, csv_path):
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    logging.info(f"✅ Data saved to {csv_path}.")

# Main scraping function
def scrape_zillow():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    logging.info("🚀 Starting Zillow Scraper...")
    driver = uc.Chrome(options=options, version_main=131)

    try:
        driver.get("https://www.zillow.com/homes/San-Francisco,-CA_rb/")
        time.sleep(5)

        load_cookies(driver)
        driver.get("https://www.zillow.com/homes/San-Francisco,-CA_rb/")
        time.sleep(5)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//article")))
        logging.info("✅ Listings loaded successfully.")

        listings = []
        page = 1

        while True:
            scroll_and_load(driver)

            elements = driver.find_elements(By.XPATH, "//article")
            logging.info(f"✅ Page {page}: Found {len(elements)} listings.")

            for element in elements:
                try:
                    price_element = element.find_elements(By.XPATH, ".//span[@data-test='property-card-price']")
                    price = price_element[0].text if price_element else "N/A"

                    address_element = element.find_elements(By.XPATH, ".//address")
                    address = address_element[0].text if address_element else "N/A"

                    details_element = element.find_elements(By.XPATH, ".//ul")
                    details_text = details_element[0].text if details_element else "N/A"
                    details = extract_details(details_text)

                    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    listings.append({
                        "price": price,
                        "address": address,
                        "bedrooms": details["bedrooms"],
                        "bathrooms": details["bathrooms"],
                        "square_feet": details["square_feet"],
                        "scraped_at": scraped_at 
                    })

                    logging.info(f"✅ Scraped listing: {address} | Price: {price} | Scraped at: {scraped_at}")

                except Exception as e:
                    logging.error(f"❌ Error processing listing: {e}")
                    continue

            if page >= 10:
                logging.info("✅ Reached the limit of 10 pages.")
                break

            if not click_next_page(driver):
                break

            page += 1

        if listings:
            csv_path = "../data/zillow_data.csv"
            save_data_to_csv(listings, csv_path)
            logging.info(f"✅ Data saved to {csv_path}. Total listings: {len(listings)}")
        else:
            logging.warning("⚠️ No listings were scraped.")

    finally:
        driver.quit()
        logging.info("🚪 WebDriver closed successfully.")

if __name__ == "__main__":
    scrape_zillow()