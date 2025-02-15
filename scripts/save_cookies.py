import pickle
import undetected_chromedriver as uc
import time
import os
import logging


# Setup Logging
log_file = "../logs/scraper.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filemode='w')

def save_cookies():
    # Force `undetected-chromedriver` to use Chrome version 131
    driver = uc.Chrome(version_main=131)

    try:
        driver.get("https://www.zillow.com/homes/San-Francisco,-CA_rb/")
        input("Manually solve CAPTCHA, then press Enter...")  # Wait for user to solve

        # Save cookies
        cookie_file_path = "../data/zillow_cookies.pkl"
        pickle.dump(driver.get_cookies(), open(cookie_file_path, "wb"))
        logging.info(f"✅ Cookies saved successfully to {cookie_file_path}.")
    except Exception as e:
        logging.error(f"❌ Error saving cookies: {e}")
    finally:
        driver.quit()
        logging.info("🚪 WebDriver closed successfully.")

if __name__ == "__main__":
    save_cookies()