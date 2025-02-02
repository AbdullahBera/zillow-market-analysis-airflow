import pickle
import undetected_chromedriver as uc
import time

# ✅ Force `undetected-chromedriver` to use Chrome version 131
driver = uc.Chrome(version_main=131)  

driver.get("https://www.zillow.com/homes/San-Francisco,-CA_rb/")
input("Manually solve CAPTCHA, then press Enter...")  # Wait for user to solve

# ✅ Save cookies
pickle.dump(driver.get_cookies(), open("../data/zillow_cookies.pkl", "wb"))
driver.quit()
print("✅ Cookies saved successfully!")
