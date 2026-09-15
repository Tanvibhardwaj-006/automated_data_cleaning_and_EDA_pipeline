import pandas as pd

def drop_full_duplicates(df, log):
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    dropped = before - after
    log.append(f"Dropped {dropped} fully duplicate rows ({before} -> {after} rows)")
    return df, log

def flag_semi_duplicates(df, key_column, log):
    key_dup = df.duplicated(subset=key_column, keep=False)
    full_dup = df.duplicated(keep=False)
    semi_dup = key_dup & ~full_dup

    df['is_semi_duplicate'] = semi_dup
    log.append(f"Flagged {semi_dup.sum()} semi-duplicate rows (same '{key_column}', differing other values)")
    return df, log

if __name__ == "__main__":
    df1 = pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    log = []
    df1, log = drop_full_duplicates(df1, log)
    df1, log = flag_semi_duplicates(df1, "order_id", log)
    print(log)