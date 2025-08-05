from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

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
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.section--white.border-grey.mdc-layout-grid'))
    )

def get_reviews_from_page():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Each review is wrapped in this div
    review_blocks = soup.select('div.section--white.border-grey.mdc-layout-grid')
    reviews = []

    def get_rating(block, label):
        try:
            rating_block = block.find('p', string=label).find_parent('div')
            width_style = rating_block.find('div', class_='rating-icons__filled')['style']
            percentage = float(width_style.replace('width:', '').replace('%', '').replace(';', '').strip())
            return round((percentage / 100) * 5, 1)
        except:
            return None

    for block in review_blocks:
        try:
            name = block.find('h6').get_text(strip=True)

            graduation_tag = block.find('span', class_='subtitle', string=lambda s: s and 'Graduated' in s)
            graduation_date = graduation_tag.get_text(strip=True).replace("Graduated: ", "") if graduation_tag else None

            # Extract review date correctly
            review_date_tag = block.select_one('div.created-at p.subtitle')
            review_date = review_date_tag.get_text(strip=True) if review_date_tag else None

            # Extract course correctly
            course = None
            course_div = block.find('div', class_='section-spacing')
            if course_div:
                p_tag = course_div.find('p')
                if p_tag:
                    course_text = p_tag.get_text(separator=' ', strip=True)
                    course = course_text.replace('Course', '').strip()

            # Extract ratings
            overall = get_rating(block, 'Overall')
            curriculum = get_rating(block, 'Curriculum')
            job_support = get_rating(block, 'Job Support')

            # Extract title correctly
            title_tag = block.select_one('div.section-spacing__top p.text--semibold.unset-margin__top')
            title = title_tag.get_text(strip=True).replace('"', '') if title_tag else None

            description_tag = block.find('div', class_='review-description')
            description = description_tag.get_text(strip=True) if description_tag else None

            reviews.append({
                'name': name,
                'graduation_date': graduation_date,
                'review_date': review_date,
                'course': course,
                'overall_rating': overall,
                'curriculum_rating': curriculum,
                'job_support_rating': job_support,
                'title': title,
                'description': description
            })
        except Exception as e:
            print(f"⚠️ Skipping review due to error: {e}")
            continue

    return reviews

# Start from page 1
url = "https://www.switchup.org/bootcamps/4geeks-academy#reviews"
driver.get(url)
wait_for_reviews()

page = 1
all_reviews = []
seen_anchors = set()

while True:
    print(f"Scraping page {page}...")
    wait_for_reviews()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    first_review_div = soup.select_one('div.section--white.border-grey.mdc-layout-grid')

    if not first_review_div:
        print("No reviews found — stopping.")
        break

    reviewer_name = first_review_div.select_one('h6.unset-margin__top.unset-margin__bottom')
    review_date = first_review_div.select_one('div.created-at p.subtitle')

    if not (reviewer_name and review_date):
        print("Reviewer name or date missing — stopping.")
        break

    anchor_text = reviewer_name.text.strip() + '|' + review_date.text.strip()

    if anchor_text in seen_anchors:
        print(f"Already scraped anchor '{anchor_text}', stopping to avoid duplicates.")
        break
    seen_anchors.add(anchor_text)

    reviews = get_reviews_from_page()
    all_reviews.extend(reviews)

    try:
        next_btns = driver.find_elements(By.CSS_SELECTOR, 'a.pagination--bound')
        next_btn = None
        for btn in next_btns:
            if btn.text.strip().startswith('Next'):
                next_btn = btn
                break

        if not next_btn:
            print("No Next button found. Stopping.")
            break

        next_page_num = int(next_btn.get_attribute('data-page'))

        if next_page_num <= page:
            print("Next page number not greater than current page — stopping.")
            break

        driver.execute_script("arguments[0].click();", next_btn)

        # Wait until the first review on the page changes (page has updated)
        WebDriverWait(driver, 10).until(lambda d: (
            (new_soup := BeautifulSoup(d.page_source, 'html.parser'))
            and (new_first_review := new_soup.select_one('div.section--white.border-grey.mdc-layout-grid'))
            and (new_name := new_first_review.select_one('h6.unset-margin__top.unset-margin__bottom'))
            and (new_date := new_first_review.select_one('div.created-at p.subtitle'))
            and (new_name.text.strip() + '|' + new_date.text.strip()) != anchor_text
        ))

        # Update anchor_text to the new page’s first review, so next loop checks against fresh anchor
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        first_review_div = soup.select_one('div.section--white.border-grey.mdc-layout-grid')
        reviewer_name = first_review_div.select_one('h6.unset-margin__top.unset-margin__bottom')
        review_date = first_review_div.select_one('div.created-at p.subtitle')
        anchor_text = reviewer_name.text.strip() + '|' + review_date.text.strip()

        page += 1

    except Exception as e:
        print(f"No next page found or error: {e}. Stopping.")
        break

driver.quit()

# Save to CSV
df = pd.DataFrame(all_reviews)
df.to_csv("switchup_reviews.csv", index=False)
print(f"✅ Scraping complete: {len(df)} reviews saved to 'switchup_reviews.csv'")
