import requests
from bs4 import BeautifulSoup
import pandas as pd
from functions import categorize_review

url = 'https://bootcamprankings.com/listings/4geeks-academy/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/113.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

comments = soup.find_all('div', class_='edgtf-comment clearfix')

reviews_data = []

for comment in comments:
    name = 'N/A'
    date = 'N/A'
    ratings = {'Rating': None, 'Curriculum': None, 'Instructors': None, 'Job Assistance': None}
    review_text = 'N/A'
    
    # Name and Date
    name_tag = comment.find('h5', class_='edgtf-comment-name')
    if name_tag:
        # The name is usually the first text node
        if name_tag.contents:
            name = name_tag.contents[0].strip()
        date_span = name_tag.find('span', class_='edgtf-comment-date-title')
        if date_span:
            date = date_span.text.strip()

    # Ratings
    rating_blocks = comment.select('div.edgtf-review-rating > span.edgtf-rating-inner')
    for block in rating_blocks:
        label_tag = block.find('span', class_='edgtf-rating-label')
        value_tag = block.find('span', class_='edgtf-rating-value')
        if label_tag and value_tag:
            category = label_tag.text.strip()
            stars = value_tag.find_all('i', class_='fas fa-star')
            ratings[category] = len(stars)
    
    # Review Text
    text_holder = comment.find('div', class_='edgtf-text-holder')
    if text_holder:
        showed_span = text_holder.find('span', class_='comment-showed')
        hidden_span = text_holder.find('span', class_='comment-hided')
        
        showed_text = showed_span.text.strip().replace('Read More', '').strip() if showed_span else ''
        hidden_text = hidden_span.text.strip().replace('Read Less', '').strip() if hidden_span else ''
        
        if showed_text and hidden_text:
            # Join carefully (avoid duplicated overlapping text)
            if showed_text.endswith(hidden_text[:20]):
                review_text = showed_text + hidden_text[20:]
            else:
                review_text = showed_text + " " + hidden_text
        elif showed_text:
            review_text = showed_text
        elif hidden_text:
            review_text = hidden_text
    
    # Collect data for this review
    review_record = {
        'Name': name,
        'Date': date,
        'Rating': ratings.get('Rating'),
        'Curriculum': ratings.get('Curriculum'),
        'Instructors': ratings.get('Instructors'),
        'Job Assistance': ratings.get('Job Assistance'),
        'Review': review_text
    }
    reviews_data.append(review_record)

# create a dataframe
df = pd.DataFrame(reviews_data)

# Apply categorization and expand dictionary into separate columns
category_df = df.apply(
    lambda row: pd.Series(categorize_review(body=row["Review"])),
    axis=1
)

# Concatenate category columns with original DataFrame
df = pd.concat([df, category_df], axis=1)

# Save to CSV using pandas
df.to_csv('bootcamprankings_reviews.csv', index=False, encoding='utf-8-sig')

print(f"Saved {len(reviews_data)} reviews to 'bootcamprankings_reviews.csv'")

