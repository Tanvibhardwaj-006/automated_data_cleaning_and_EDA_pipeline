import pandas as pd 

def drop_full_duplicates(df,log):
    before= len(df)
    df = df.drop_duplicates()
    after=len(df)
    dropped= before-after
    log.append(f" dropped {dropped} fully duplicated rows {before} -> {after}")

    return df,log

def flag_semi_duplicates(df,key_column,log):
    key_dup= df.duplicated(subset=key_column,keep=False)
    full_dup = df.duplicated(keep=False)
    semi_dup = key_dup & ~ full_dup

    df['is_semi_duplicate'] = semi_dup
    log.append(f"Flagged {semi_dup.sum()} semi-duplicate rows (same '{key_column}', differing other values)")
    return df, log


if __name__ == "__main__":
    df1=pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    log=[]
    df1,log=drop_full_duplicates(df1,log)
    df1,log=flag_semi_duplicates(df1,'order_id',log)
    print(log)

def handle_missing_values(df,log):
    
    
    missing_values= df.isnull().sum()
    for column in df.columns:
        null_perc= (missing_values[column]/len(df))*100
        print(f"CHECKING: {column} -> {null_perc:.2f}%")
        if null_perc >=100:
            df= df.drop(columns=column)
            log.append(f"Dropped column '{column}' with {null_perc:.2f}% missing values")
        elif null_perc>40:
            log.append(f"Flagged column '{column}' — {null_perc:.2f}% missing, needs manual review")
        elif null_perc<40 and null_perc>0:
            if df[column].dtype in ['int64','float64']:
                uniqueness_ratio = df[column].nunique() / len(df)
                if uniqueness_ratio>0.90:
                    log.append(f"Flagged column '{column}' — {null_perc:.2f}% missing, high uniqueness ratio ({uniqueness_ratio:.2f}), needs manual review")
                else:
                    median_val = df[column].median()
                    df[column] = df[column].fillna(median_val)
                    log.append(f"Filled {missing_values[column]} nulls in '{column}' with median ({median_val})")
        elif null_perc==0:
            log.append(f"Column '{column}' has no missing values")
        else:
            log.append(f"Column '{column}' has {null_perc:.2f}% missing values — no fill strategy applied yet (non-numeric)")
    return df,log

df2 = pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/retail_store_sales.csv")
log2 = []
df2, log2 = handle_missing_values(df2, log2)
print(log2)


print(len(log2), len(df2.columns))

