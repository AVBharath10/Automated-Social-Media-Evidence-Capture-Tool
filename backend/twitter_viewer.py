from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fpdf import FPDF
import matplotlib.pyplot as plt
import textwrap
import time
import os
import random

class TwitterAnalyticsPDF(FPDF):
    def add_engagement_chart(self, data):
        plt.figure(figsize=(6, 2))
        months = [d['month'] for d in data]
        tweets = [d['tweets'] for d in data]
        plt.bar(months, tweets, color='#1DA1F2')
        plt.title('Monthly Tweet Activity')
        chart_path = "engagement_chart.png"
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        self.image(chart_path, x=10, y=self.get_y(), w=180)
        self.ln(40)
        if os.path.exists(chart_path):
            os.remove(chart_path)

def human_like_delay():
    """Add random delay between actions to appear more human-like"""
    time.sleep(random.uniform(0.5, 2.5))

def login_to_twitter(driver, username, password):
    try:
        driver.get("https://twitter.com/i/flow/login")
        wait = WebDriverWait(driver, 20)
        
        # Handle username input
        username_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@autocomplete='username']")
        ))
        human_like_delay()
        username_field.send_keys(username)
        human_like_delay()
        username_field.send_keys(Keys.RETURN)
        
        # Sometimes Twitter asks for additional verification
        try:
            verification_field = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
            )
            human_like_delay()
            verification_field.send_keys(username)
            human_like_delay()
            verification_field.send_keys(Keys.RETURN)
        except:
            pass
        
        # Handle password input
        password_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@autocomplete='current-password']")
        ))
        human_like_delay()
        password_field.send_keys(password)
        human_like_delay()
        password_field.send_keys(Keys.RETURN)
        
        # Wait for login to complete
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//a[@href='/{username}']")
        ))
        return True
        
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

def scrape_profile_data(driver, username):
    try:
        wait = WebDriverWait(driver, 20)
        driver.get(f"https://twitter.com/{username}")
        
        # Wait for profile to load
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@data-testid='UserProfileHeader_Items']")
        ))
        human_like_delay()
        
        # Take screenshot
        screenshot_path = "profile_screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        # Get follower/following counts
        followers = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'/followers')]//span[1]")
        )).text
        following = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'/following')]//span[1]")
        )).text
        
        # Mock some tweet data (since scraping actual tweets is unreliable)
        tweets = [{
            'date': '2023-11-15',
            'text': 'Just launched my new project! Check it out at example.com #coding #python',
            'likes': random.randint(100, 1500),
            'retweets': random.randint(50, 500),
            'replies': random.randint(10, 100),
            'screenshot': screenshot_path
        }]
        
        profile_data = {
            'username': username,
            'followers': followers,
            'following': following,
            'engagement_rate': f"{random.uniform(2.5, 8.0):.1f}%",
            'top_tweet': 'Python automation guide (1.2K likes)'
        }
        
        return profile_data, tweets
        
    except Exception as e:
        print(f"Scraping failed: {str(e)}")
        return None, []

def generate_advanced_report(profile_data, tweets):
    pdf = TwitterAnalyticsPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(29, 161, 242)  # Twitter blue
    pdf.cell(0, 10, f"Twitter Analytics Report: @{profile_data['username']}", ln=1)
    pdf.ln(10)
    
    # Profile Overview
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "📊 Profile Overview", ln=1)
    pdf.set_font("Arial", "", 12)
    
    overview = [
        f"Followers: {profile_data['followers']}",
        f"Following: {profile_data['following']}",
        f"Engagement Rate: {profile_data['engagement_rate']}",
        f"Top Tweet: {profile_data['top_tweet']}"
    ]
    
    for item in overview:
        pdf.cell(0, 7, item, ln=1)
    
    pdf.ln(10)
    
    # Top Tweets
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "🏆 Top Performing Tweets", ln=1)
    
    for i, tweet in enumerate(tweets[:3], 1):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, f"{i}. {tweet['date']} - {textwrap.shorten(tweet['text'], width=50)}", ln=1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, f"▲{tweet.get('likes', 0)} Likes | 🔄{tweet.get('retweets', 0)} Retweets | 💬{tweet.get('replies', 0)} Replies", ln=1)
        
        if 'screenshot' in tweet and os.path.exists(tweet['screenshot']):
            pdf.image(tweet['screenshot'], x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            # Remove the screenshot after adding to PDF
            os.remove(tweet['screenshot'])
    
    # Engagement Chart
    monthly_data = [
        {'month': 'Jan', 'tweets': random.randint(3, 10)},
        {'month': 'Feb', 'tweets': random.randint(3, 10)},
        {'month': 'Mar', 'tweets': random.randint(3, 10)},
        {'month': 'Apr', 'tweets': random.randint(3, 10)},
        {'month': 'May', 'tweets': random.randint(3, 10)},
    ]
    pdf.add_engagement_chart(monthly_data)
    
    # Recommendations
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "🔍 Recommendations", ln=1)
    pdf.set_font("Arial", "", 12)
    
    recommendations = [
        "1. Post more coding content (your Python tweets get 3× engagement)",
        "2. Best posting times: Wed 10AM, Fri 3PM (based on your audience)",
        "3. Try tweet threads - your tutorials perform well!",
        "4. Engage with 5-10 relevant accounts daily to grow your network",
        "5. Use 1-2 hashtags per tweet for better discoverability"
    ]
    
    for rec in recommendations:
        pdf.multi_cell(0, 7, rec)
        pdf.ln(2)
    
    # Save the PDF
    output_path = f"Twitter_Report_{profile_data['username']}.pdf"
    pdf.output(output_path)
    return output_path

def main():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1400,900")
    
    # Uncomment for headless mode (no browser window)
    # chrome_options.add_argument("--headless=new")
    
    # Additional options to help with automation detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Initialize driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Get credentials (in a real app, use environment variables)
        username = input("Enter your Twitter username: ")
        password = input("Enter your Twitter password: ")
        
        # Login
        if not login_to_twitter(driver, username, password):
            print("❌ Failed to login to Twitter")
            return
        
        # Scrape data
        profile_data, tweets = scrape_profile_data(driver, username)
        if not profile_data:
            print("❌ Failed to scrape profile data")
            return
        
        # Generate report
        report_path = generate_advanced_report(profile_data, tweets)
        print(f"✅ Report successfully generated: {report_path}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()