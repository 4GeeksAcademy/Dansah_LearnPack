from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from functions import categorize_review

# Setup headless browser
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

def expand_all_read_more_buttons():
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-action='click->toggle#toggle']")
        print(f"Found {len(buttons)} Read More buttons on this page.")

        for i, btn in enumerate(buttons, 1):
            if btn.is_displayed():
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)  # Increase delay for animation
                except Exception as e:
                    print(f"⚠️ Could not click Read More button #{i}: {e}")
            else:
                print(f"Read More button #{i} not visible, skipping.")
    except Exception as e:
        print(f"⚠️ Error finding Read More buttons: {e}")


def get_reviews_from_page():
    expand_all_read_more_buttons() 
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    review_blocks = soup.select('ul.divide-y.divide-gray.divide-solid > li')
    reviews = []

    expected_categories = ['overall_experience', 'curriculum', 'job_assistance', 'instructors']

    filled_star_path_d = "M12 .587l3.668 7.568L24 9.306l-6.064 5.828 1.48 8.279L12 19.446l-7.417 3.967 1.481-8.279L0 9.306l8.332-1.151z"

    for block in review_blocks:
        name = block.select_one('span.font-medium')
        role = block.select_one('div.flex.text-gray-medium span')
        verification = block.select_one('div.text-green div')
        date = block.select_one('div.text-gray-medium.flex-shrink-0')
        headline = block.select_one('h3.text-gray-darkest.font-medium')
        # body_container = block.select_one('div[data-controller="toggle"]')
        # review_text = body_container.get_text(separator=' ', strip=True) if body_container else None
        body_container = block.select_one('div[data-controller="toggle"]')
        if body_container:
            # Find all divs that have data-toggle-target="content"
            content_divs = body_container.select('div[data-toggle-target="content"]')
            # Join the text from all those divs (usually 2 divs: truncated and full)
            review_text = ' '.join(div.get_text(separator=' ', strip=True) for div in content_divs)
        else:
            review_text = None

        review_data = {
            'name': name.text.strip() if name else None,
            'role': role.text.strip() if role else None,
            'verification': verification.text.strip() if verification else None,
            'date': date.text.strip() if date else None,
            'headline': headline.text.strip() if headline else None,
            'review_body': review_text
        }

        # Initialize all expected rating fields with None
        for cat in expected_categories:
            review_data[cat] = None

        # Extract rating info
        rating_grid = block.select_one('div.bg-gray-light.grid')
        if rating_grid:
            rating_items = rating_grid.select('div.grid.grid-cols-2')
            for item in rating_items:
                category_divs = item.select('div')
                if len(category_divs) >= 2:
                    category = category_divs[0].text.strip().lower().replace(" ", "_")
                    star_container = category_divs[1]

                    # Count filled stars by checking path d attribute
                    stars = star_container.select('svg')
                    filled_stars_count = 0
                    for star in stars:
                        path = star.find('path')
                        if path and path.get('d') == filled_star_path_d:
                            filled_stars_count += 1

                    if category in expected_categories:
                        review_data[category] = filled_stars_count

        reviews.append(review_data)

    return reviews

# Start from page 1
url = "https://www.coursereport.com/schools/4geeks-academy/reviews"
driver.get(url)
wait_for_reviews()

all_reviews = []
page = 1

seen_first_review = None

while True:
    print(f"Scraping page {page}...")
    wait_for_reviews()
    reviews = get_reviews_from_page()

    if reviews:
        first_anchor = (reviews[0]['name'], reviews[0]['date'])
        if first_anchor == seen_first_review:
            print("Duplicate page detected. Stopping.")
            break
        seen_first_review = first_anchor
        all_reviews.extend(reviews)
    else:
        print("No reviews found. Stopping.")
        break

    try:
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

# create a dataframe
df = pd.DataFrame(all_reviews)

# Apply categorization and expand dictionary into separate columns
category_df = df.apply(
    lambda row: pd.Series(categorize_review(row.get("headline"), row.get("review_body"))),
    axis=1
)

# Concatenate category columns with original DataFrame
df = pd.concat([df, category_df], axis=1)

#save the data
df.to_csv("course_report_reviews.csv", index=False)

print(f"✅ Scraping complete: {len(df)} reviews saved to 'course_report_reviews.csv'")
