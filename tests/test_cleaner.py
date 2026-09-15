import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from cleaner import drop_full_duplicates, flag_semi_duplicates

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

if __name__ == "__main__":
    test_drop_full_duplicates()
    test_flag_semi_duplicates()