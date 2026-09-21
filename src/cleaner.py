import pandas as pd 
pd.set_option('future.no_silent_downcasting', True)

# completeness 

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



def handle_missing_values(df,log):
    
    
    missing_values= df.isnull().sum()
    for column in df.columns:
        null_perc= (missing_values[column]/len(df))*100

        if null_perc ==100:
            df= df.drop(columns=column)
            log.append(f"Dropped column '{column}' with {null_perc:.2f}% missing values")
        elif null_perc>40:
            log.append(f"Flagged column '{column}' — {null_perc:.2f}% missing, needs manual review")
        elif null_perc<=40 and null_perc>0:
            unique_vals = df[column].dropna().unique()
            if len(unique_vals) == 2 and set(unique_vals) <= {True, False}:
                df[column] = df[column].fillna(False).astype(bool)
                log.append(f"Filled {missing_values[column]} nulls in '{column}' with False (boolean-like column, missing interpreted as False)")
            elif df[column].dtype in ['int64','float64']:
                uniqueness_ratio = df[column].nunique() / len(df)
                if uniqueness_ratio>=0.90:
                    log.append(f"Flagged column '{column}' — {null_perc:.2f}% missing, high uniqueness ratio ({uniqueness_ratio:.2f}), needs manual review")
                else:
                    median_val = df[column].median()
                    df[column] = df[column].fillna(median_val)
                    log.append(f"Filled {missing_values[column]} nulls in '{column}' with median ({median_val})")
            else:
                df[column] = df[column].fillna('Unknown')
                log.append(f"Column '{column}' has {null_perc:.2f}% missing values — filled with 'Unknown'")
        elif null_perc == 0:
            log.append(f"Column '{column}' has no missing values")
    return df, log

def fix_dtypes(df, log):
    for column in df.columns:
        if df[column].dtype == 'object':
            try:
                # quick sample check first 
                sample = df[column].dropna().head(20)
                sample_converted = pd.to_datetime(sample, errors='coerce', format='mixed')
                sample_success_rate = sample_converted.notna().sum() / len(sample) if len(sample) > 0 else 0

                if sample_success_rate < 0.5:
                    continue 

                converted = pd.to_datetime(df[column], errors='coerce', format='mixed')
                success_rate = converted.notna().sum() / len(df)

                if success_rate >= 0.8:
                    failed_count = converted.isna().sum() - df[column].isna().sum()
                    df[column] = converted
                    log.append(f"Converted column '{column}' to datetime (success rate: {success_rate:.2f}, {failed_count} values could not be parsed and became NaT)")

            except Exception as e:
                log.append(f"Column '{column}' could not be evaluated for datetime conversion ({type(e).__name__})")
                continue

    return df, log
            


 



if __name__ == "__main__":
    df1=pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    log=[]
    df1,log=drop_full_duplicates(df1,log)
    df1,log=flag_semi_duplicates(df1,'order_id',log)
    df1,log=fix_dtypes(df1,log)
    print(df1.dtypes)
    print(log)

    




