def profile_dataset(df,name):
    profile={
        'name':name,
        'row_count':df.shape[0],
        'column_count':df.shape[1],
        'duplicate rows':df.duplicated().sum(),
        'null count':df.isnull().sum().to_dict(),
        'null percent':(df.isnull().sum()/len(df)*100).round(2).to_dict(),
        'dtypes':df.dtypes.astype(str).to_dict()
    }
    print(f"df name--{name}")
    print(f"row_count:{profile['row_count']} , column_count:{profile['column_count']}")
    print(f"duplicate rows:{profile['duplicate rows']}")
    print(f"nulls per columns")
    for col,pct in profile['null percent'].items():
        print(f"{col}: {profile['null count'][col]} ({pct}%)")

    return profile

if __name__ == "__main__":
    import pandas as pd

    df1 = pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/olist_orders_dataset.csv")
    df2 = pd.read_csv(r"C:/Users/Aone/Desktop/retail project/data/raw/retail_store_sales.csv")

    profile_dataset(df1, "olist_orders")
    profile_dataset(df2, "retail_sales")