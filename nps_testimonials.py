from functions import categorize_review
import pandas as pd
pd.set_option('display.max_columns', None)

# create a dataframe
df = pd.read_csv("/workspaces/Dansah_LearnPack/nps_reviews.csv")

# Apply categorization and expand dictionary into separate columns
category_df = df.apply(
    lambda row: pd.Series(categorize_review(body=row["comment"])),
    axis=1
)

# Concatenate category columns with original DataFrame
df = pd.concat([df, category_df], axis=1)

#save the data
df.to_csv("nps_reviews.csv", index=False)