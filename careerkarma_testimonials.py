import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# -------------------------
# Configuration
# -------------------------
URL_SCHOOL = "https://careerkarma.com/schools/4geeks-academy/"
EMAIL = os.getenv("CK_EMAIL")
PASSWORD = os.getenv("CK_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Please set CK_EMAIL and CK_PASSWORD environment variables.")

# -------------------------
# Selenium Setup
# -------------------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless=new")  # remove headless if debugging
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

# -------------------------
# 1️⃣ Log in
# -------------------------
driver.get("https://careerkarma.com/sign-in/")

wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.CSS_SELECTOR, "button[data-qa='sign-in-form_sign-in-btn']").click()

# Wait for login to complete
wait.until(EC.url_contains("careerkarma.com"))
print("✅ Logged in successfully")

# -------------------------
# 2️⃣ Navigate to School Page and Reviews
# -------------------------
driver.get(URL_SCHOOL)
reviews_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Reviews')]")))
reviews_tab.click()
time.sleep(2)

# Click "See all reviews" if present
try:
    see_all_btn = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa='schools-page_reviews-section_see-all-reviews-btn']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", see_all_btn)
    driver.execute_script("arguments[0].click();", see_all_btn)
    print("➡️ Clicked 'See all reviews'")
    time.sleep(2)
except:
    print("⚠️ 'See all reviews' button not found, proceeding...")

# -------------------------
# 3️⃣ Load all reviews
# -------------------------
prev_count = 0
while True:
    reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='schools-page_reviews-section_school-review']")
    current_count = len(reviews)
    
    try:
        load_more_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa='schools-page_reviews-section_load-more-btn']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
        driver.execute_script("arguments[0].click();", load_more_btn)
        print("➡️ Clicked 'Load More'")
        time.sleep(2)  # wait for new reviews to render
        
        reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='schools-page_reviews-section_school-review']")
        if len(reviews) == prev_count:
            print("✅ All reviews loaded, no new reviews appeared.")
            break
        prev_count = len(reviews)
        
    except:
        print("✅ 'Load More' button not found or clickable, ending loop.")
        break

print(f"Total reviews loaded: {len(reviews)}")

# -------------------------
# 4️⃣ Expand all "See more" texts
# -------------------------
for see_more in driver.find_elements(By.CSS_SELECTOR, "label.sc-86822f03-0"):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", see_more)
        driver.execute_script("arguments[0].click();", see_more)
        time.sleep(0.1)
    except:
        continue
print("✅ All review texts expanded")

# -------------------------
# 5️⃣ Parse reviews
# -------------------------
soup = BeautifulSoup(driver.page_source, "html.parser")
review_cards = soup.select("div[data-qa='schools-page_reviews-section_school-review']")
print(f"Parsing {len(review_cards)} reviews...")

# -------------------------
# 6️⃣ Save to CSV
# -------------------------
with open("careerkarma_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Name", "Role", "Date", "Title", "Review",
        "Overall", "Instructors", "Curriculum", "Job Assistance"
    ])

    for card in review_cards:
        name_tag = card.select_one("span.sc-aefd771a-3")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        role_tag = card.select_one("span.sc-aefd771a-3 span")
        role = role_tag.get_text(strip=True) if role_tag else "N/A"

        date_tag = card.select_one("div.sc-18449bc4-1")
        date = date_tag.get_text(strip=True) if date_tag else "N/A"

        review_text_tag = card.select_one("div.sc-18449bc4-21")
        review_text = review_text_tag.get_text(strip=True) if review_text_tag else "N/A"

        # Ratings
        def get_rating(label):
            tag = card.select_one(f"span[data-qa='review-card_rating-{label}']")
            return tag.get_text(strip=True) if tag else "N/A"

        overall = get_rating("overall")
        instructors = get_rating("instructors")
        curriculum = get_rating("curriculum")
        job_assistance = get_rating("job_assistance")

        writer.writerow([name, role, date, "", review_text,
                         overall, instructors, curriculum, job_assistance])

print("✅ Reviews saved to careerkarma_reviews.csv")

driver.quit()

