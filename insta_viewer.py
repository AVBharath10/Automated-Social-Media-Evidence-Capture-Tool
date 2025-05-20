from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from fpdf import FPDF
from PIL import Image

# ---- Setup ----
INSTAGRAM_USERNAME = 'barou._.sh'
INSTAGRAM_PASSWORD = 'naveen10##'

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

driver = webdriver.Chrome()
driver.get("https://www.instagram.com/")

wait = WebDriverWait(driver, 15)

# ---- Login ----
username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
username_input.send_keys(INSTAGRAM_USERNAME)
password_input.send_keys(INSTAGRAM_PASSWORD)
password_input.send_keys(Keys.RETURN)

# ---- Wait for login to complete by waiting for profile icon to appear ----
try:
    profile_icon = wait.until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Profile photo']")))
    print("Login successful!")
except Exception as e:
    print("Login may have failed or took too long:", e)

# ---- Skip 'Save Your Login Info?' popup ----
try:
    not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
    not_now.click()
    time.sleep(2)
except:
    pass

# ---- Skip 'Turn on Notifications' popup ----
try:
    not_now_notifications = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
    not_now_notifications.click()
    time.sleep(2)
except:
    pass

# ---- Navigate to Profile ----
driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/")

# Wait for profile page to load
try:
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
    print("Profile page loaded.")
except Exception as e:
    print("Profile page may not have loaded correctly:", e)

time.sleep(3)  # extra wait to be safe

# Screenshot 1: Profile Page
profile_path = os.path.join(output_dir, "profile.png")
driver.save_screenshot(profile_path)
print(f"Profile screenshot saved to {profile_path}")

# ---- Followers ----
try:
    followers_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "followers")))
    followers_link.click()
    time.sleep(3)
    followers_path = os.path.join(output_dir, "followers.png")
    driver.save_screenshot(followers_path)
    print(f"Followers screenshot saved to {followers_path}")
    # Close popup
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(text(), 'Close')] | //div[@role='dialog']//div[contains(@aria-label, 'Close')]")))
    close_button.click()
    time.sleep(2)
except Exception as e:
    print("Followers section failed.", e)

# ---- Following ----
try:
    following_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "following")))
    following_link.click()
    time.sleep(3)
    following_path = os.path.join(output_dir, "following.png")
    driver.save_screenshot(following_path)
    print(f"Following screenshot saved to {following_path}")
    # Close popup
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(text(), 'Close')] | //div[@role='dialog']//div[contains(@aria-label, 'Close')]")))
    close_button.click()
    time.sleep(2)
except Exception as e:
    print("Following section failed.", e)

driver.quit()

# ---- Generate PDF ----
pdf = FPDF()
for img_file in sorted(os.listdir(output_dir)):
    if img_file.endswith(".png"):
        image_path = os.path.join(output_dir, img_file)
        cover = Image.open(image_path)
        width, height = cover.size
        width, height = float(width * 0.264583), float(height * 0.264583)  # px to mm
        pdf.add_page()
        pdf.image(image_path, 0, 0, width, height)

pdf_path = os.path.join(output_dir, "Instagram_Report.pdf")
pdf.output(pdf_path, "F")
print(f"✅ Report generated: {pdf_path}")
