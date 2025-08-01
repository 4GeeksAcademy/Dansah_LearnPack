from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_reviews():
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.divide-y.divide-gray.divide-solid > li'))
    )

def get_reviews_from_page():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    review_blocks = soup.select('ul.divide-y.divide-gray.divide-solid > li')
    reviews = []

    for block in review_blocks:
        name = block.select_one('span.font-medium')
        role = block.select_one('div.flex.text-gray-medium span')
        verification = block.select_one('div.text-green div')
        date = block.select_one('div.text-gray-medium.flex-shrink-0')
        headline = block.select_one('h3.text-gray-darkest.font-medium')
        body = block.select_one('div[data-controller="toggle"] > div')

        reviews.append({
            'name': name.text.strip() if name else None,
            'role': role.text.strip() if role else None,
            'verification': verification.text.strip() if verification else None,
            'date': date.text.strip() if date else None,
            'headline': headline.text.strip() if headline else None,
            'review_body': body.text.strip() if body else None
        })
    return reviews

# Start from page 1
url = "https://www.coursereport.com/schools/4geeks-academy/reviews"
driver.get(url)
wait_for_reviews()

all_reviews = []
page = 1

while True:
    print(f"Scraping page {page}...")
    wait_for_reviews()
    reviews = get_reviews_from_page()
    all_reviews.extend(reviews)

    try:
        # Find and click the next button if it exists and is enabled
        next_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[rel="next"]:not(.disabled)'))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        page += 1
        time.sleep(2.5)
    except Exception:
        print("No active 'Next' button found. Reached last page.")
        break

driver.quit()

# Save to CSV
df = pd.DataFrame(all_reviews)
df.to_csv("course_report_reviews.csv", index=False)
print(f"✅ Scraping complete: {len(df)} reviews saved to 'course_report_reviews.csv'")

