import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from fpdf import FPDF
from PIL import Image

if len(sys.argv) < 3:
    print("Usage: python insta_viewer.py <username> <password>")
    sys.exit(1)

INSTAGRAM_USERNAME = sys.argv[1]
INSTAGRAM_PASSWORD = sys.argv[2]

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

driver = webdriver.Chrome()
driver.get("https://www.instagram.com/")
wait = WebDriverWait(driver, 15)

username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
username_input.send_keys(INSTAGRAM_USERNAME)
password_input.send_keys(INSTAGRAM_PASSWORD)
password_input.send_keys(Keys.RETURN)

try:
    profile_icon = wait.until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Profile photo']")))
    print("Login successful!")
except Exception as e:
    print("Login may have failed or took too long:", e)

# Handle pop-ups
for _ in range(2):
    try:
        not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
        not_now.click()
        time.sleep(2)
    except:
        pass

# Visit user profile
driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/")
try:
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
    print("Profile page loaded.")
except Exception as e:
    print("Profile page may not have loaded correctly:", e)

time.sleep(3)

# Profile screenshot
profile_path = os.path.join(output_dir, "profile.png")
driver.save_screenshot(profile_path)
print(f"Profile screenshot saved to {profile_path}")

def close_dialog():
    try:
        # Try different ways to close the dialog
        close_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//*[contains(@aria-label, 'Close') or contains(text(), 'Close')]")
        for btn in close_buttons:
            try:
                btn.click()
                time.sleep(1)
                return True
            except:
                continue
        # If above fails, try pressing ESC
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ESCAPE)
        time.sleep(1)
        return True
    except:
        return False

# Followers screenshot
try:
    followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'followers')]")))
    followers_link.click()
    time.sleep(3)
    followers_path = os.path.join(output_dir, "followers.png")
    driver.save_screenshot(followers_path)
    print(f"Followers screenshot saved to {followers_path}")
    
    # Ensure dialog is closed
    if not close_dialog():
        print("Warning: Could not close followers dialog properly")
    time.sleep(2)
except Exception as e:
    print("Followers section failed.", e)

# Following screenshot
try:
    following_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'following')]")))
    following_link.click()
    time.sleep(3)
    following_path = os.path.join(output_dir, "following.png")
    driver.save_screenshot(following_path)
    print(f"Following screenshot saved to {following_path}")
    
    # Ensure dialog is closed
    if not close_dialog():
        print("Warning: Could not close following dialog properly")
    time.sleep(2)
except Exception as e:
    print("Following section failed.", e)

# Scroll to load posts and take screenshots
try:
    print("Capturing posts...")
    # First make sure we're back at the top of the profile page
    driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/")
    time.sleep(3)
    
    for i in range(3):  # Scroll 3 times
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(3)
        post_path = os.path.join(output_dir, f"posts_scroll_{i+1}.png")
        driver.save_screenshot(post_path)
        print(f"Post screenshot saved to {post_path}")
except Exception as e:
    print("Post section failed.", e)

driver.quit()

# Generate PDF
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
print(f"Report generated: {pdf_path}")