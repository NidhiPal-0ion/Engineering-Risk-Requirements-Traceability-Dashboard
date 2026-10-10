import pandas as pd
import pytest
from src.traceability_engine import (
    extract_req_ids_from_text,
    build_traceability_matrix,
    calculate_coverage_metrics
)

def test_extract_req_ids_regex():
    text = "Validating REQ-BLD-001 and REQ-BLD-003 in extreme load test"
    found = extract_req_ids_from_text(text)
    assert "REQ-BLD-001" in found
    assert "REQ-BLD-003" in found

def test_traceability_matrix_building():
    req_data = pd.DataFrame([
        {"req_id": "REQ-001", "description": "Spar tension", "subsystem": "Spar Cap", "severity": "HIGH"},
        {"req_id": "REQ-002", "description": "Root fatigue", "subsystem": "Root Joint", "severity": "HIGH"},
        {"req_id": "REQ-003", "description": "LPS grounding", "subsystem": "LPS", "severity": "HIGH"}
    ])
    
    test_data = pd.DataFrame([
        {"test_id": "TEST-01", "test_name": "Bending Test", "status": "PASSED", "req_id": "REQ-001", "description": "Validates REQ-001"},
        {"test_id": "TEST-02", "test_name": "Fatigue Test", "status": "FAILED", "req_id": "REQ-002", "description": "Validates REQ-002"}
    ])
    
    trace_df = build_traceability_matrix(req_data, test_data)
    assert len(trace_df) == 3
    
    req1_status = trace_df.loc[trace_df["req_id"] == "REQ-001", "verification_status"].values[0]
    req2_status = trace_df.loc[trace_df["req_id"] == "REQ-002", "verification_status"].values[0]
    req3_status = trace_df.loc[trace_df["req_id"] == "REQ-003", "verification_status"].values[0]
    
    assert req1_status == "VERIFIED_PASS"
    assert req2_status == "VERIFIED_FAIL"
    assert req3_status == "UNTESTED"

def test_calculate_coverage_metrics():
    trace_df = pd.DataFrame([
        {"verification_status": "VERIFIED_PASS"},
        {"verification_status": "VERIFIED_FAIL"},
        {"verification_status": "UNTESTED"},
        {"verification_status": "UNTESTED"}
    ])
    metrics = calculate_coverage_metrics(trace_df)
    assert metrics["total_requirements"] == 4
    assert metrics["coverage_pct"] == 50.0  # 2 out of 4 tested
    assert metrics["pass_rate_pct"] == 25.0  # 1 out of 4 passed
    assert metrics["untested_count"] == 2
    assert metrics["failed_count"] == 1
