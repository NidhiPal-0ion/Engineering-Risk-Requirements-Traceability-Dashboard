import pandas as pd
import pytest
from src.risk_engine import (
    calculate_risk_score,
    generate_action_recommendation,
    apply_risk_scoring
)

def test_risk_score_calculation():
    # Failed test on Spar Cap (High severity) should yield highest risk (CRITICAL)
    raw_s, norm_s, level = calculate_risk_score("HIGH", "Spar Cap", "VERIFIED_FAIL")
    assert level == "CRITICAL"
    assert norm_s == 100.0  # Max score
    
    # Passed test should yield low risk
    raw_s_pass, norm_s_pass, level_pass = calculate_risk_score("LOW", "Trailing Edge", "VERIFIED_PASS")
    assert level_pass == "LOW"
    assert norm_s_pass < 30.0

def test_untested_high_severity_risk_level():
    # Untested High severity on Root Joint should yield CRITICAL or HIGH risk
    _, norm_s, level = calculate_risk_score("HIGH", "Root Joint", "UNTESTED")
    assert level in ["CRITICAL", "HIGH"]

def test_action_recommendation():
    act_fail = generate_action_recommendation("HIGH", "Root Joint", "VERIFIED_FAIL", "CRITICAL")
    assert "URGENT REDESIGN" in act_fail
    
    act_untested = generate_action_recommendation("HIGH", "Spar Cap", "UNTESTED", "HIGH")
    assert "URGENT TEST MAPPING" in act_untested
    
    act_pass = generate_action_recommendation("LOW", "Trailing Edge", "VERIFIED_PASS", "LOW")
    assert "COMPLIANT" in act_pass

def test_apply_risk_scoring():
    trace_df = pd.DataFrame([
        {"req_id": "REQ-01", "severity": "HIGH", "subsystem": "Spar Cap", "verification_status": "VERIFIED_FAIL"},
        {"req_id": "REQ-02", "severity": "LOW", "subsystem": "Trailing Edge", "verification_status": "VERIFIED_PASS"}
    ])
    scored_df = apply_risk_scoring(trace_df)
    assert "risk_score" in scored_df.columns
    assert "risk_level" in scored_df.columns
    assert "recommended_action" in scored_df.columns
    # Sort order check: highest risk first
    assert scored_df.iloc[0]["req_id"] == "REQ-01"
