import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from cleaner import drop_full_duplicates, fix_dtypes, flag_semi_duplicates, handle_missing_values

def test_drop_full_duplicates():
    test_df = pd.DataFrame({
        "order_id": ["A1", "A1", "A2"],
        "status": ["delivered", "delivered", "cancelled"]
    })
    result_df, log = drop_full_duplicates(test_df, [])
    assert len(result_df) == 2, f"Expected 2 rows, got {len(result_df)}"
    print("test_drop_full_duplicates passed")

def test_flag_semi_duplicates():
    test_df = pd.DataFrame({
        "order_id": ["A1", "A1", "A2", "A2", "A3"],
        "status":   ["delivered", "delivered", "delivered", "cancelled", "delivered"]
    })
    result_df, log = flag_semi_duplicates(test_df, "order_id", [])
    flags = result_df["is_semi_duplicate"].tolist()
    assert flags == [False, False, True, True, False], f"Got {flags}"
    print("test_flag_semi_duplicates passed")

def test_handle_missing_values():
    test_df = pd.DataFrame({
    "Amount": [10, 20, np.nan, 40, 50, np.nan, 70, 80, np.nan, 100],
    "Is_Returned": [True, False, np.nan, True, np.nan, False,True, False,np.nan,True],
    "Category": ["A", "B", np.nan, "A", "C", np.nan,"Unknown","A","B","C"],
    "Transaction_ID": [1001, 1002, np.nan, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    "Needs_Review": [1, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 8, np.nan, np.nan],
    "Empty_Column": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
})
    result_df, log = handle_missing_values(test_df, [])
    assert result_df["Amount"].iloc[2] == 50, f"Expected median 50, got {result_df['Amount'].iloc[2]}"
    assert result_df["Is_Returned"].iloc[2] == False, "Missing Is_Returned not filled with False"
    assert result_df["Category"].isnull().sum() == 0, "Category column still has nulls"
    assert result_df["Is_Returned"].dtype == bool, "Is_Returned column is not boolean"
    assert result_df["Category"].iloc[2] == "Unknown", "Category column nulls not filled with 'Unknown'"
    assert any("Transaction_ID" in entry and "high uniqueness" in entry for entry in log), "Transaction_ID not flagged as identifier"
    assert result_df["Transaction_ID"].isnull().sum() == 1, "Transaction_ID should be flagged, not filled"
    assert  any("Needs_Review" in entry and "manual review" in entry for entry in log), "Needs_Review not flagged for manual review"
    assert any("Empty_Column" in entry for entry in log), "100% null column is not dropped"
    print("test_handle_missing_values passed")

def test_fix_dtypes():
    test_df=pd.DataFrame({
        "Order_Date": [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
        "2024-01-06",
        "2024-01-07",
        "2024-01-08",
        "not a date",
        "2024-01-10"
    ],
    "Category": [
        "Food",
        "Clothing",
        "Food",
        "Books",
        "Food",
        "Books",
        "Clothing",
        "Food",
        "Books",
        "Clothing"
    ],
    "Customer_Note": [
        "2024-02-01",
        "hello",
        "good",
        "2024-02-04",
        "nice",
        "bad",
        "2024-02-07",
        "okay",
        "fine",
        "great"
    ],
    "Messy_Date": 
    [
        "2024-01-01",
        "hello",
        "???",
        "@@@",
        "not-a-date",
        "blah blah ",
        "zumbaaaaa",
        "knock knock ",
        "tinkerbell",
        "rapunzel"
    ]
    })

def test_flag_faulty_dates():
    test_df=pd.DataFrame({
        "
    })

if __name__ == "__main__":
    test_drop_full_duplicates()
    test_flag_semi_duplicates()
    test_handle_missing_values()
    test_fix_dtypes()