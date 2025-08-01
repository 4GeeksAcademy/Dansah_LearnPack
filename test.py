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

def extract_rating(section, label):
    try:
        # Find the <p> tag with the correct label
        label_tag = section.find('p', class_='rating-type', string=label)
        if not label_tag:
            return None

        # Get the parent <div> of the label and locate the filled rating bar
        rating_div = label_tag.find_parent('div', class_='review-scores')
        filled = rating_div.select_one('.rating-icons__filled')

        if filled and 'style' in filled.attrs:
            width_str = filled['style'].split(':')[-1].strip().replace('%', '')
            return round(float(width_str) / 20, 1)
    except Exception:
        return None

def get_reviews_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    reviews_data = []

    # Review info
    review_blocks = soup.select('div.section--white.border-grey.mdc-layout-grid')

    for block in review_blocks:
        name_tag = block.select_one('h6.unset-margin__top.unset-margin__bottom')
        name = name_tag.text.strip() if name_tag else None
        
        # Course
        course_tag = block.select_one('p.unset-margin__bottom > span.text--semibold')
        if course_tag and course_tag.text.strip() == 'Course':
            course_info_tag = course_tag.find_next_sibling(text=True)
            course = course_info_tag.strip() if course_info_tag else None
        else:
            course = None

        # Date
        date_tag = block.select_one('div.created-at p.subtitle')
        date = date_tag.text.strip() if date_tag else None

        # Headline
        headline_tag = block.select_one('p.text--semibold.unset-margin__top span')
        headline = headline_tag.text.strip() if headline_tag else None

        # Body
        body_tag = block.select_one('div.review-description')
        review_body = body_tag.text.strip() if body_tag else None

        # Ratings Section
        rating_section = div.select_one('span.section-spacing')
        overall = extract_rating(rating_section, 'Overall')
        curriculum = extract_rating(rating_section, 'Curriculum')
        job_support = extract_rating(rating_section, 'Job Support')


        reviews_data.append({
            'name': name,
            'course': course,
            'date': date,
            'headline': headline,
            'review_body': review_body,
            'overall_rating': overall,
            'curriculum_rating': curriculum,
            'job_support_rating': job_support
        })

    return reviews_data

# Main scraping loop
all_reviews = []
for page in range(1, 21):  # Adjust page range if needed
    url = f"https://www.switchup.org/chimera/v2/school-review-list?path=%2Fbootcamps%2F4geeks-academy&schoolId=10492&perPage=10&simpleHtml=true&truncationLength=250&readMoreOmission=...&page={page}"
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers)
    reviews_on_page = get_reviews_from_page(response.text)
    all_reviews.extend(reviews_on_page)
    time.sleep(random.uniform(1, 3))  

# Save as DataFrame
df = pd.DataFrame(all_reviews)
print(df.head())
#df.to_csv('course_report_reviews.csv', index=False)
