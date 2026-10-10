import os
import pandas as pd
from typing import Tuple, Optional

REQUIRED_REQ_COLUMNS = ["req_id", "description", "subsystem", "severity"]
REQUIRED_TEST_COLUMNS = ["test_id", "test_name", "status"]

VALID_SEVERITIES = ["HIGH", "MEDIUM", "LOW"]
VALID_STATUSES = ["PASSED", "FAILED", "IN_PROGRESS", "NOT_STARTED"]

def load_requirements_csv(file_path_or_buffer) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Loads and validates engineering requirements CSV.
    Returns (DataFrame, error_message_or_None).
    """
    try:
        df = pd.read_csv(file_path_or_buffer)
    except Exception as e:
        return pd.DataFrame(), f"Failed to read CSV file: {str(e)}"
    
    # Standardize column names to lowercase stripped
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    missing_cols = [col for col in REQUIRED_REQ_COLUMNS if col not in df.columns]
    if missing_cols:
        return pd.DataFrame(), f"Missing required columns in Requirements CSV: {', '.join(missing_cols)}"
    
    # Fill NA and clean string values
    df["req_id"] = df["req_id"].astype(str).str.strip().str.upper()
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df["subsystem"] = df["subsystem"].fillna("General").astype(str).str.strip()
    df["severity"] = df["severity"].fillna("Medium").astype(str).str.strip().str.upper()
    
    # Validate severity values
    df["severity"] = df["severity"].apply(lambda s: s if s in VALID_SEVERITIES else "MEDIUM")
    
    # Remove empty req_ids
    df = df[df["req_id"] != ""].copy()
    
    return df, None

def load_test_matrix_csv(file_path_or_buffer) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Loads and validates test execution matrix CSV.
    Returns (DataFrame, error_message_or_None).
    """
    try:
        df = pd.read_csv(file_path_or_buffer)
    except Exception as e:
        return pd.DataFrame(), f"Failed to read CSV file: {str(e)}"
    
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    missing_cols = [col for col in REQUIRED_TEST_COLUMNS if col not in df.columns]
    if missing_cols:
        return pd.DataFrame(), f"Missing required columns in Test Matrix CSV: {', '.join(missing_cols)}"
    
    df["test_id"] = df["test_id"].astype(str).str.strip().str.upper()
    df["test_name"] = df["test_name"].fillna("").astype(str).str.strip()
    df["status"] = df["status"].fillna("NOT_STARTED").astype(str).str.strip().str.upper()
    
    if "req_id" in df.columns:
        df["req_id"] = df["req_id"].fillna("").astype(str).str.strip().str.upper()
    else:
        df["req_id"] = ""
        
    if "description" in df.columns:
        df["description"] = df["description"].fillna("").astype(str).str.strip()
    else:
        df["description"] = ""
        
    df["status"] = df["status"].apply(lambda s: s if s in VALID_STATUSES else "NOT_STARTED")
    df = df[df["test_id"] != ""].copy()
    
    return df, None

def get_default_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns sample requirements and test matrix DataFrames for wind-turbine blade engineering."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req_path = os.path.join(base_dir, "data", "sample_requirements.csv")
    test_path = os.path.join(base_dir, "data", "sample_test_matrix.csv")
    
    req_df, _ = load_requirements_csv(req_path)
    test_df, _ = load_test_matrix_csv(test_path)
    return req_df, test_df
