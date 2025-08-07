from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def extract_review_data(review_div):
    # Reviewer info
    reviewer = review_div.select_one('div.p7f0Nd a.yC3ZMb')
    if not reviewer:
        return None
    
    name = reviewer.select_one('div.Vpc5Fe').text.strip() if reviewer.select_one('div.Vpc5Fe') else None
    profile_url = reviewer.get('href', None)
    num_reviews = reviewer.select_one('div.GSM50').text.strip() if reviewer.select_one('div.GSM50') else None
    profile_img_style = reviewer.select_one('div.wSokxc')['style'] if reviewer.select_one('div.wSokxc') else ''
    profile_img_url = re.search(r'url\("([^"]+)"\)', profile_img_style)
    profile_img_url = profile_img_url.group(1) if profile_img_url else None

    # Rating and date
    rating_div = review_div.select_one('div.k0Ysuc div.dHX2k')
    stars = len(rating_div.find_all('svg')) if rating_div else None
    date = review_div.select_one('div.k0Ysuc span.y3Ibjb').text.strip() if review_div.select_one('div.k0Ysuc span.y3Ibjb') else None

    # Review text
    review_text = review_div.select_one('div.OA1nbd').text.strip() if review_div.select_one('div.OA1nbd') else None

    return {
        'name': name,
        'profile_url': profile_url,
        'num_reviews': num_reviews,
        'profile_img_url': profile_img_url,
        'stars': stars,
        'date': date,
        'review_text': review_text
    }

def main():
    url = "https://www.google.com/search?sca_esv=50347784169c3c85&hl=en&authuser=0&sxsrf=AE3TifPRPkMonRKhE9fIyyOQpKznneQJHA:1754530295486&si=AMgyJEtREmoPL4P1I5IDCfuA8gybfVI2d5Uj7QMwYCZHKDZ-E0avZvxuce6GVx3_9-D_fr6M0gI-0WeckzEERl50p8UilH8NbOSalriKY1qTKuRR08CaAFgOcQXRXe5aaHDgvPo2Wkm8OkHyoOi_m3Pw5NFmXzN-qA%3D%3D&q=4Geeks+Academy+Chile+Reviews&sa=X&ved=2ahUKEwjfkYrYxveOAxW8FDQIHe6gKYcQ0bkNegQIJBAE&biw=1366&bih=714&dpr=2"

    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Click "More user reviews" repeatedly
    while True:
        try:
            more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ZFiwCf span.LGwnxb.JGD2rd')))
            more_button.click()
            time.sleep(3)
        except Exception:
            print("No more 'More user reviews' button found or cannot click.")
            break

    # Parse loaded HTML with BeautifulSoup
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    # Find all review containers (based on your example structure)
    review_divs = soup.select('div.p7f0Nd')  # This selects the reviewer info div, need parent container

    # Because 'p7f0Nd' is nested inside the full review container, get the parent of each
    # Let's get all parents with review blocks by going up two divs or so:
    full_reviews = []
    for div in review_divs:
        parent = div.parent
        # Try going up until we find the div containing the review text div 'OA1nbd'
        while parent and not parent.select_one('div.OA1nbd'):
            parent = parent.parent
        if parent and parent not in full_reviews:
            full_reviews.append(parent)

    # Extract data for each review
    for i, review_div in enumerate(full_reviews, 1):
        data = extract_review_data(review_div)
        if data:
            print(f"Review #{i}:")
            print(f"Name: {data['name']}")
            print(f"Profile URL: {data['profile_url']}")
            print(f"Number of reviews by reviewer: {data['num_reviews']}")
            print(f"Profile Image URL: {data['profile_img_url']}")
            print(f"Stars: {data['stars']}")
            print(f"Date: {data['date']}")
            print(f"Review Text: {data['review_text']}")
            print("-" * 80)

if __name__ == "__main__":
    main()



