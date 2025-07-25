import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


all_reviews = []

# HTTP request headers to mimic a real user's web browser.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
]

# scrape the CourseReport page
def get_reviews_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    reviews_data = []

    # ✅ Match the full review container
    review_containers = soup.select('div.flex.flex-col.gap-4')

    for review in review_containers:
        # --- Metadata ---
        name_tag = review.select_one('span.font-medium')
        name = name_tag.text.strip() if name_tag else None

        role_tag = review.select_one('div.flex.text-gray-medium span')
        role = role_tag.text.strip() if role_tag else None

        verify_tag = review.select_one('div.text-green div')
        verification = verify_tag.text.strip() if verify_tag else None

        date_tag = review.select_one('div.text-gray-medium.flex-shrink-0')
        date = date_tag.text.strip() if date_tag else None

        # --- Headline ---
        headline_tag = review.select_one('h3.text-gray-darkest.font-medium')
        headline = headline_tag.text.strip() if headline_tag else None

        # --- Review Body ---
        body_tag = review.select_one('div[data-controller="toggle"] > div')
        review_body = body_tag.text.strip() if body_tag else None

        # --- Ratings ---
        ratings = {}
        rating_sections = review.select('div.bg-gray-light div.grid.grid-cols-2')
        for section in rating_sections:
            try:
                category = section.select_one('div:nth-child(1)').text.strip()
                stars = len(section.select('svg.text-orange'))
                ratings[category] = stars
            except Exception:
                continue

        # --- Final Review Dictionary ---
        reviews_data.append({
            'name': name,
            'role': role,
            'verification': verification,
            'date': date,
            'headline': headline,
            'review_body': review_body,
            'ratings': ratings
        })

    return reviews_data


# Main scraping loop
all_reviews = []
for page in range(1, 15):  # Adjust page range if needed
    url = f"https://www.coursereport.com/schools/4geeks-academy/reviews?reviews_page={page}"
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers)
    reviews_on_page = get_reviews_from_page(response.text)
    all_reviews.extend(reviews_on_page)
    time.sleep(random.uniform(1, 3))  

# Save as DataFrame
df = pd.DataFrame(all_reviews)
print(df.head())

#df.to_json("reviews.json", indent=2)





