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


# HTTP request headers to mimic a real user's web browser.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

# scrape the web page
def scrape_coursereport_reviews(business_url, pages=5):
    headers = get_random_headers()

    reviews = []

    for page in range(1, pages+1):
        url = f"{business_url}?page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for review in soup.select('div.styles_reviewContent__0Q2Tg'):
            title = review.select_one('h2').text.strip() if review.select_one('h2') else ''
            content = review.select_one('p').text.strip() if review.select_one('p') else ''
            rating_element = review.select_one('div.star-rating')
            rating = rating_element['data-rating'] if rating_element else ''
            reviews.append({
                'title': title,
                'content': content,
                'rating': rating
            })

        time.sleep(random.uniform(1, 3))  # Be kind to servers

    return pd.DataFrame(reviews)

# Example usage
# df = scrape_trustpilot_reviews('https://www.trustpilot.com/review/example.com')


