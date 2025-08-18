import pandas as pd


# create a dataframe
df = pd.readcsv("/workspaces/Dansah_LearnPack/nps_reviews.csv")

# Apply categorization and expand dictionary into separate columns
category_df = df.apply(
    lambda row: pd.Series(categorize_review(row.get("title"), row.get("description"))),
    axis=1
)

# Concatenate category columns with original DataFrame
df = pd.concat([df, category_df], axis=1)

#save the data
df.to_csv("nps_reviews.csv", index=False)