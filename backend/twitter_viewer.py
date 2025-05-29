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
    print("Usage: python twitter_viewer.py <username> <password>")
    sys.exit(1)

TWITTER_USERNAME = sys.argv[1]
TWITTER_PASSWORD = sys.argv[2]

output_dir = "twitter_output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

driver = webdriver.Chrome()
driver.get("https://twitter.com/i/flow/login")
wait = WebDriverWait(driver, 15)

try:
    # Twitter login flow can be more complex
    username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']")))
    username_input.send_keys(TWITTER_USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(2)
    
    # Sometimes Twitter asks for unusual things
    try:
        # Handle case where Twitter asks "Is this you?"
        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(., 'This is me')]")))
        confirm_button.click()
        time.sleep(2)
    except:
        pass
    
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='current-password']")))
    password_input.send_keys(TWITTER_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    
    # Wait for home timeline to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/home']")))
    print("Login successful!")
except Exception as e:
    print("Login failed:", e)
    driver.quit()
    sys.exit(1)

# Go to profile
driver.get(f"https://twitter.com/{TWITTER_USERNAME}")
time.sleep(3)

profile_path = os.path.join(output_dir, "profile.png")
driver.save_screenshot(profile_path)
print(f"Profile screenshot saved to {profile_path}")

def close_dialog():
    try:
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ESCAPE)
        time.sleep(1)
        return True
    except:
        return False

# Capture followers
try:
    followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@href='/{TWITTER_USERNAME}/followers']")))
    followers_link.click()
    time.sleep(3)
    followers_path = os.path.join(output_dir, "followers.png")
    driver.save_screenshot(followers_path)
    print(f"Followers screenshot saved to {followers_path}")
    
    if not close_dialog():
        print("Warning: Could not close followers dialog properly")
    time.sleep(2)
except Exception as e:
    print("Followers section failed.", e)

# Capture following
try:
    following_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@href='/{TWITTER_USERNAME}/following']")))
    following_link.click()
    time.sleep(3)
    following_path = os.path.join(output_dir, "following.png")
    driver.save_screenshot(following_path)
    print(f"Following screenshot saved to {following_path}")
    
    if not close_dialog():
        print("Warning: Could not close following dialog properly")
    time.sleep(2)
except Exception as e:
    print("Following section failed.", e)

# Capture tweets
try:
    print("Capturing tweets...")
    driver.get(f"https://twitter.com/{TWITTER_USERNAME}")
    time.sleep(3)
    
    for i in range(3):  # Scroll 3 times
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(3)
        tweet_path = os.path.join(output_dir, f"tweets_scroll_{i+1}.png")
        driver.save_screenshot(tweet_path)
        print(f"Tweet screenshot saved to {tweet_path}")
except Exception as e:
    print("Tweet section failed.", e)

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

pdf_path = os.path.join(output_dir, "Twitter_Report.pdf")
pdf.output(pdf_path, "F")
print(f"Report generated: {pdf_path}")