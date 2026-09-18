import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from cleaner import drop_full_duplicates, flag_semi_duplicates, handle_missing_values

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
    "Amount": [10, 20, np.nan, 40, 50, np.nan],
    "Is_Returned": [True, False, np.nan, True, np.nan, False],
    "Category": ["A", "B", np.nan, "A", "C", np.nan],
    "Transaction_ID": ["T001", "T002", "T003", "T004", "T005",np.nan]
})
    result_df, log = handle_missing_values(test_df, [])
    assert result_df["Amount"].iloc[2] == 30, f"Expected median 30, got {result_df['Amount'].iloc[2]}"
    assert result_df["Is_Returned"].iloc[2] == False, "Missing Is_Returned not filled with False"
    assert result_df["Category"].isnull().sum() == 0, "Category column still has nulls"
    assert result_df["Is_Returned"].dtype == bool, "Is_Returned column is not boolean"
    assert result_df["Category"].iloc[2] == "Unknown", "Category column nulls not filled with 'Unknown'"
    assert any("Transaction_ID" in entry and "high uniqueness" in entry for entry in log), "Transaction_ID not flagged as identifier"
    assert result_df["Transaction_ID"].isnull().sum() == 1, "Transaction_ID should be flagged, not filled"
    print("test_handle_missing_values passed")
   

if __name__ == "__main__":
    test_drop_full_duplicates()
    test_flag_semi_duplicates()
    test_handle_missing_values()