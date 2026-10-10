import io
import pandas as pd
import pytest
from src.data_loader import (
    load_requirements_csv,
    load_test_matrix_csv,
    get_default_sample_data,
    REQUIRED_REQ_COLUMNS,
    REQUIRED_TEST_COLUMNS
)

def test_load_valid_requirements():
    csv_data = """req_id,description,subsystem,severity
REQ-001,Blade root strain check,Root Joint,High
REQ-002,Spar cap tension,Spar Cap,Medium
"""
    df, err = load_requirements_csv(io.StringIO(csv_data))
    assert err is None
    assert len(df) == 2
    assert "REQ-001" in df["req_id"].values
    assert df.loc[df["req_id"] == "REQ-001", "severity"].values[0] == "HIGH"

def test_load_invalid_requirements_missing_col():
    csv_data = """req_id,description
REQ-001,Blade root strain check
"""
    df, err = load_requirements_csv(io.StringIO(csv_data))
    assert df.empty
    assert err is not None
    assert "Missing required columns" in err

def test_load_valid_test_matrix():
    csv_data = """test_id,test_name,status,req_id,description
TEST-001,Flapwise Bending,PASSED,REQ-001,Tested REQ-001
"""
    df, err = load_test_matrix_csv(io.StringIO(csv_data))
    assert err is None
    assert len(df) == 1
    assert df.iloc[0]["test_id"] == "TEST-001"
    assert df.iloc[0]["status"] == "PASSED"

def test_default_sample_data_loader():
    req_df, test_df = get_default_sample_data()
    assert not req_df.empty
    assert not test_df.empty
    for col in REQUIRED_REQ_COLUMNS:
        assert col in req_df.columns
    for col in REQUIRED_TEST_COLUMNS:
        assert col in test_df.columns
