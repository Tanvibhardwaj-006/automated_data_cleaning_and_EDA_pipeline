def drop_full_duplicates(df, log):
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    dropped = before - after

    log.append(f"Dropped {dropped} fully duplicate rows ({before} -> {after} rows)")

    return df, log

if __name__ == "__main__":
    import pandas as pd
    df1 = pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    test_log = []
    df1, test_log = drop_full_duplicates(df1, test_log)
    print(test_log)

    def flag_semi_duplicates(df, key_column, log):
        key_dup=df.duplicated(key_column, keep=False)
        full_dup=df.duplicated(keep=False)
        semi_dup=key_dup & ~full_dup

        df['semi_duplicate_flag'] = semi_dup
        log.append(f"flagged{semi_dup.sum()} column {key_column} same but different other columns")
        return df,log



test_df = pd.DataFrame({
    "order_id": ["A1", "A1", "A2", "A2", "A3"],
    "status":   ["delivered", "delivered", "delivered", "cancelled", "delivered"]
})
# A1 rows are full duplicates (identical) -> should NOT be flagged semi
# A2 rows share key but differ -> SHOULD be flagged semi
# A3 is unique -> not flagged

test_log = []
result_df, test_log = flag_semi_duplicates(test_df, "order_id", test_log)
print(result_df)
print(test_log)