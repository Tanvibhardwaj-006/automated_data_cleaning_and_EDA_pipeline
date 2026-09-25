
import string

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
            if df[column].dtype == 'datetime64[ns]':
                log.append(f"Column '{column}' has {missing_values[column]} missing dates (NaT) — left as-is, missingness treated as meaningful")
            else:
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
            

def flag_faulty_dates(df, log):
    known_cols = {'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date'}
    if not known_cols & set(df.columns):
        log.append("No known sequential date columns found for this dataset — faulty-date check skipped")
        return df, log
    for column in df.select_dtypes(include=['datetime64[ns]']).columns:
        if df[column].isnull().any():
            log.append(f"Column '{column}' has NaT values, which may indicate parsing issues or missing dates")
    if 'order_purchase_timestamp' in df.columns and 'order_approved_at' in df.columns:
        faulty_approval = df['order_approved_at'] < df['order_purchase_timestamp']
        log.append(f"Flagged {faulty_approval.sum()} rows where 'order_approved_at' is before 'order_purchase_timestamp'")
    if 'order_delivered_carrier_date' in df.columns and 'order_approved_at' in df.columns:
        faulty_carrier = df['order_approved_at'] > df['order_delivered_carrier_date']
        log.append(f"Flagged {faulty_carrier.sum()} rows where 'order_approved_at' is after 'order_delivered_carrier_date'")
    if 'order_delivered_customer_date' in df.columns and 'order_delivered_carrier_date' in df.columns:
        faulty_customer = df['order_delivered_carrier_date'] > df['order_delivered_customer_date']
        log.append(f"Flagged {faulty_customer.sum()} rows where 'order_delivered_carrier_date' is after 'order_delivered_customer_date'")

    return df, log

def normalize_text_columns(df,log):
    for column in df.columns:
        if df[column].dtype=='object':
            uniqueness_ratio = df[column].nunique() / len(df)
            if uniqueness_ratio>=0.90:
                log.append(f"column: {column} has high uniqueness ratio ({uniqueness_ratio:.2f}), classifying it as a identifier")
            else:
                df[column] = df[column].str.strip().str.lower().str.strip(string.punctuation).str.strip()
                log.append(f"column: {column} has been normalized")
    return df,log


def derive_missing_values(df, log):
    subset_cols = ['Price Per Unit', 'Quantity', 'Total Spent']
    if not all(col in df.columns for col in subset_cols):
        log.append("Derivation columns not found in this dataset — skipping derivation step")
        return df, log

    mask_price = df['Price Per Unit'].isnull() & df['Quantity'].notnull() & df['Total Spent'].notnull()
    df.loc[mask_price, 'Price Per Unit'] = df.loc[mask_price, 'Total Spent'] / df.loc[mask_price, 'Quantity']
    log.append(f"Derived {mask_price.sum()} 'Price Per Unit' values from Total Spent / Quantity")

    mask_quantity = df['Quantity'].isnull() & df['Price Per Unit'].notnull() & df['Total Spent'].notnull()
    df.loc[mask_quantity, 'Quantity'] = df.loc[mask_quantity, 'Total Spent'] / df.loc[mask_quantity, 'Price Per Unit']
    log.append(f"Derived {mask_quantity.sum()} 'Quantity' values from Total Spent / Price Per Unit")

    mask_total_spent = df['Total Spent'].isnull() & df['Price Per Unit'].notnull() & df['Quantity'].notnull()
    df.loc[mask_total_spent, 'Total Spent'] = df.loc[mask_total_spent, 'Price Per Unit'] * df.loc[mask_total_spent, 'Quantity']
    log.append(f"Derived {mask_total_spent.sum()} 'Total Spent' values from Price Per Unit * Quantity")

    return df, log


def clean_dataset(df, key_column, log=None):
    if log is None:
        log = []
    df,log=drop_full_duplicates(df,log)
    df,log=flag_semi_duplicates(df,key_column,log)
    df,log=fix_dtypes(df,log)
    df,log=handle_missing_values(df,log)   
    df,log=flag_faulty_dates(df,log)
    df, log = normalize_text_columns(df, log)
    return df, log




if __name__ == "__main__":
    df1=pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    df1,log=clean_dataset(df1,"order_id")
    print(log)
    df2=pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/retail_store_sales.csv")
    df2,log=clean_dataset(df2,"Transaction ID")
    print(log)
    




