import sys
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
from PIL import Image

# ======================
# UTILITY FUNCTIONS
# ======================
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_metadata(output_dir, url, username):
    metadata = {
        "platform": "Instagram",
        "url": url,
        "investigated_account": username,
        "capture_time": datetime.now().isoformat(),
        "tool": "Social Media Forensic Tool v1.1"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

def log_action(log_file, action, status="SUCCESS", error=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "error": str(error)[:500] if error else None  # Truncate long errors
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry  # Return for PDF inclusion

def create_pdf(output_dir, username, log_entries):
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    
    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Instagram Forensic Report", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
    pdf.cell(0, 10, f"Investigated Account: @{username}", ln=1)
    pdf.ln(20)
    
    # Screenshot Pages
    for img_file in sorted(os.listdir(output_dir)):
        if img_file.endswith(".png"):
            pdf.add_page()
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Evidence: {img_file.replace('.png', '')}", ln=1)
            
            image_path = os.path.join(output_dir, img_file)
            img = Image.open(image_path)
            w, h = img.size
            ratio = min((190)/w, (250)/h) * 0.264583  # Scaled with margins
            pdf.image(image_path, x=10, y=30, w=w*ratio, h=h*ratio)
    
    # Audit Log Page
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Forensic Audit Log", ln=1)
    pdf.set_font("Courier", "", 10)
    
    for entry in log_entries:
        pdf.multi_cell(0, 7, 
                      f"{entry['timestamp']} | {entry['action']} | {entry['status']}\n"
                      f"Error: {entry['error'] or 'None'}\n"
                      "-"*60)
    
    pdf.output(os.path.join(output_dir, f"Instagram_Report_{username}.pdf"))

# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python insta_forensic.py <username> <password>")
        sys.exit(1)

    INSTAGRAM_USERNAME = sys.argv[1]
    INSTAGRAM_PASSWORD = sys.argv[2]
    
    # Setup output
    output_dir = f"instagram_evidence_{INSTAGRAM_USERNAME}_{get_timestamp()}"
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "forensic_audit.log")
    log_entries = []
    
    # Configure Chrome to avoid "Save Login Info" prompt
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    
    try:
        # Initialize
        driver = webdriver.Chrome(options=chrome_options)
        log_entries.append(log_action(log_file, "Initialize WebDriver"))
        
        # Login with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                driver.get("https://www.instagram.com/")
                wait = WebDriverWait(driver, 20 if attempt == 0 else 40)  # Longer wait on retry
                
                # Handle cookie popup (EU)
                try:
                    accept_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, 
                        "//button[contains(text(), 'Allow essential and optional cookies')]")))
                    accept_cookies.click()
                    log_entries.append(log_action(log_file, "Cookie consent"))
                except:
                    pass
                
                # Login
                username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
                username_input.send_keys(INSTAGRAM_USERNAME)
                password_input.send_keys(INSTAGRAM_PASSWORD)
                password_input.send_keys(Keys.RETURN)
                log_entries.append(log_action(log_file, "Login attempt"))
                
                # Handle "Save Login Info" prompt
                try:
                    not_now = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//div[contains(text(), 'Not now')]")))
                    not_now.click()
                    log_entries.append(log_action(log_file, "Dismissed 'Save Login' prompt"))
                    time.sleep(2)
                except:
                    pass
                
                # Verify login
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@aria-label, 'Home')]")))
                log_entries.append(log_action(log_file, "Login verification"))
                break  # Success
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                log_entries.append(log_action(log_file, f"Login attempt {attempt+1}", "RETRYING", e))
                time.sleep(5)
        
        # Go to profile
        driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/")
        time.sleep(3)
        save_metadata(output_dir, driver.current_url, INSTAGRAM_USERNAME)
        log_entries.append(log_action(log_file, "Profile page loaded"))
        
        # Capture elements with error handling
        capture_points = [
            ("profile_header", "//header"),
            ("posts", "//article"),
            ("followers", "//a[contains(@href, 'followers')]"),
            ("following", "//a[contains(@href, 'following')]")
        ]
        
        for name, xpath in capture_points:
            try:
                if name in ["followers", "following"]:
                    driver.find_element(By.XPATH, xpath).click()
                    time.sleep(2)
                
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                driver.save_screenshot(os.path.join(output_dir, f"{name}_{get_timestamp()}.png"))
                log_entries.append(log_action(log_file, f"Captured {name}"))
                
                if name in ["followers", "following"]:
                    driver.find_element(By.XPATH, "//*[@aria-label='Close']").click()
                    time.sleep(1)
                    
            except Exception as e:
                log_entries.append(log_action(log_file, f"Capture {name}", "FAILED", e))
        
    except Exception as e:
        log_entries.append(log_action(log_file, "Main execution", "CRITICAL FAILURE", e))
        print(f"Error occurred: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            log_entries.append(log_action(log_file, "Browser closed"))
    
    # Generate PDF with integrated logs
    create_pdf(output_dir, INSTAGRAM_USERNAME, log_entries)
    print(f"\nInvestigation complete. Results saved to: {os.path.abspath(output_dir)}")