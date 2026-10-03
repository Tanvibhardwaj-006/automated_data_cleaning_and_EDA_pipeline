import pandas as pd

df = pd.read_csv("data/raw/olist_orders_dataset.csv").head(1000)
dupes = df.sample(20, random_state=42)
corrupted = pd.concat([df, dupes], ignore_index=True)
corrupted.to_csv("data/raw/olist_sample_with_duplicates.csv", index=False)