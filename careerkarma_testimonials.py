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
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
load_dotenv()

# BEFORE RUNNING THIS FILE RUN THE FOLLOWING COMMANDS IN THE TERMINAL:
# export CK_EMAIL="your@email.com"
# export CK_PASSWORD="yourpassword"

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
        time.sleep(2)
        
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
# 5️⃣ Parse reviews and save to CSV
# -------------------------
review_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='schools-page_reviews-section_school-review']")
print(f"Writing {len(review_elements)} reviews to CSV...")

with open("careerkarma_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Name", "Role", "Date", "Title", "Review",
        "Overall", "Instructors", "Curriculum", "Job Assistance"
    ])
    
    actions = ActionChains(driver)

    for idx, review_el in enumerate(review_elements, start=1):
        soup_card = BeautifulSoup(review_el.get_attribute("outerHTML"), "html.parser")

        # --- Static fields ---
        name_tag = soup_card.select_one("span.sc-aefd771a-3")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        role_tag = soup_card.select_one("span.sc-aefd771a-3 span")
        role = role_tag.get_text(strip=True) if role_tag else "N/A"

        date_tag = soup_card.select_one("div.sc-18449bc4-1")
        date = date_tag.get_text(strip=True) if date_tag else "N/A"

        title_tag = soup_card.select_one("p.sc-18449bc4-4")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        review_text_tag = soup_card.select_one("div.sc-18449bc4-21")
        review_text = review_text_tag.get_text(strip=True) if review_text_tag else "N/A"

        # --- Dynamic ratings ---
        overall = instructors = curriculum = job_assistance = "N/A"

        try:
            overall_star_imgs = review_el.find_elements(By.CSS_SELECTOR, "img[alt='star'][type='review']")
            overall = sum(1 for img in overall_star_imgs if "star-checked" in img.get_attribute("src"))

            try:
                more_arrow = WebDriverWait(review_el, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='more']"))
                )
                actions.move_to_element(more_arrow).perform()
                time.sleep(0.5)

                dropdowns = review_el.find_elements(By.CSS_SELECTOR, "div[type='starsDropdown']")
                for dd in dropdowns:
                    try:
                        label = dd.find_element(By.XPATH, "./preceding-sibling::span").text.strip().lower()
                    except:
                        label = ""
                    stars = dd.find_elements(By.CSS_SELECTOR, "img[src*='bootcamps-star-checked.png']")
                    filled = len(stars)
                    if "instructors" in label:
                        instructors = filled
                    elif "curriculum" in label:
                        curriculum = filled
                    elif "job assistance" in label:
                        job_assistance = filled

            except:
                pass

        except Exception as e:
            print(f"⚠️ Ratings error on review #{idx}: {e}")

        # --- Write row ---
        writer.writerow([name, role, date, title, review_text,
                         overall, instructors, curriculum, job_assistance])

print("✅ Reviews saved to careerkarma_reviews.csv")
driver.quit()
