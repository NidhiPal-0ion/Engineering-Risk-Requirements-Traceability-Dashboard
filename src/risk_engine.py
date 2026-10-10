import pandas as pd
from typing import Dict, List, Tuple

SEVERITY_WEIGHTS = {
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0
}

SUBSYSTEM_WEIGHTS = {
    "SPAR CAP": 1.5,
    "ROOT JOINT": 1.5,
    "SHEAR WEB": 1.3,
    "LIGHTNING PROTECTION SYSTEM (LPS)": 1.2,
    "LPS": 1.2,
    "AERODYNAMIC SHELL": 1.1,
    "TRAILING EDGE": 1.0
}

VERIFICATION_MULTIPLIERS = {
    "VERIFIED_FAIL": 2.5,
    "UNTESTED": 2.0,
    "IN_PROGRESS": 1.2,
    "VERIFIED_PASS": 0.5
}

# Maximum possible raw score = 3.0 (High) * 1.5 (Spar/Root) * 2.5 (Fail) = 11.25
MAX_RAW_RISK_SCORE = 11.25

def calculate_risk_score(severity: str, subsystem: str, verification_status: str) -> Tuple[float, float, str]:
    """
    Calculates raw risk score, normalized score (0-100), and risk priority level.
    
    Formula:
      Raw Risk = Severity Weight * Subsystem Weight * Verification Status Multiplier
      Normalized Risk = Min(100, (Raw Risk / 11.25) * 100)
    """
    sev_clean = str(severity).strip().upper()
    sub_clean = str(subsystem).strip().upper()
    ver_clean = str(verification_status).strip().upper()
    
    s_weight = SEVERITY_WEIGHTS.get(sev_clean, 2.0)
    
    # Subsystem weight matching (fuzzy or direct key match)
    sub_weight = 1.0
    for key, weight in SUBSYSTEM_WEIGHTS.items():
        if key in sub_clean or sub_clean in key:
            sub_weight = weight
            break
            
    v_mult = VERIFICATION_MULTIPLIERS.get(ver_clean, 2.0)
    
    raw_score = s_weight * sub_weight * v_mult
    norm_score = min(100.0, round((raw_score / MAX_RAW_RISK_SCORE) * 100.0, 1))
    
    if norm_score >= 70.0:
        level = "CRITICAL"
    elif norm_score >= 50.0:
        level = "HIGH"
    elif norm_score >= 30.0:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return round(raw_score, 2), norm_score, level

def generate_action_recommendation(severity: str, subsystem: str, verification_status: str, risk_level: str) -> str:
    """
    Generates actionable engineering recommendations based on verification status and risk level.
    """
    ver_clean = str(verification_status).strip().upper()
    sev_clean = str(severity).strip().upper()
    
    if ver_clean == "VERIFIED_FAIL":
        return f"URGENT REDESIGN: Verification test FAILED for {subsystem}. Initiate root-cause analysis and structural margin review."
    elif ver_clean == "UNTESTED":
        if sev_clean == "HIGH" or risk_level in ["CRITICAL", "HIGH"]:
            return f"URGENT TEST MAPPING: High-risk requirement lacks verification coverage. Assign test protocol immediately."
        else:
            return f"TRACEABILITY GAP: Missing test mapping. Define verification method and map test case."
    elif ver_clean == "IN_PROGRESS":
        return f"MONITOR: Verification test in progress. Expedite lab execution and log test evidence."
    elif ver_clean == "VERIFIED_PASS":
        return f"COMPLIANT: Requirement verified and passed. Maintain compliance baseline document."
    else:
        return f"REVIEW: Audit requirement status and update verification matrix."

def apply_risk_scoring(trace_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies risk calculation and recommendation logic across all requirements in trace DataFrame.
    """
    df = trace_df.copy()
    
    raw_scores = []
    norm_scores = []
    risk_levels = []
    actions = []
    
    for _, row in df.iterrows():
        sev = row.get("severity", "MEDIUM")
        sub = row.get("subsystem", "General")
        ver = row.get("verification_status", "UNTESTED")
        
        raw_s, norm_s, level = calculate_risk_score(sev, sub, ver)
        action = generate_action_recommendation(sev, sub, ver, level)
        
        raw_scores.append(raw_s)
        norm_scores.append(norm_s)
        risk_levels.append(level)
        actions.append(action)
        
    df["raw_risk_score"] = raw_scores
    df["risk_score"] = norm_scores
    df["risk_level"] = risk_levels
    df["recommended_action"] = actions
    
    # Sort by risk score descending so highest risk items appear first
    df = df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    return df
