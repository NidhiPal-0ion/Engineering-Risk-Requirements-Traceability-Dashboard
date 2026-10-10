import re
import pandas as pd
from typing import Dict, List, Set, Tuple

def extract_req_ids_from_text(text: str) -> Set[str]:
    """
    Uses regular expressions to extract requirement IDs (e.g., REQ-BLD-001 or REQ-001)
    from free-text test descriptions, comments, or matrices.
    Inspired by regex parsing patterns in requirements-traceability-engine.
    """
    if not isinstance(text, str):
        return set()
    
    # Matches patterns like REQ-BLD-001, REQ-001, REQ-SYS-123
    pattern = r"\bREQ-[A-Z0-9]+(?:-[A-Z0-9]+)*\b"
    matches = re.findall(pattern, text.upper())
    return set(matches)

def build_traceability_matrix(req_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cross-references system requirements with test matrix execution records.
    Maps requirements via explicit req_id column or regex extraction from test descriptions.
    
    Returns an aggregated DataFrame with one row per requirement, including mapped tests,
    aggregated verification status, and coverage details.
    """
    reqs = req_df.copy()
    
    # Pre-parse mappings from test_df
    test_mappings: Dict[str, List[Dict]] = {}
    
    for _, test_row in test_df.iterrows():
        t_id = test_row.get("test_id", "")
        t_name = test_row.get("test_name", "")
        t_status = test_row.get("status", "NOT_STARTED")
        t_desc = test_row.get("description", "")
        explicit_req = test_row.get("req_id", "")
        
        target_reqs = set()
        if explicit_req:
            # Handle comma or space separated req_ids if present
            for part in re.split(r"[,;\s]+", explicit_req):
                if part:
                    target_reqs.add(part.upper())
        
        # Regex extraction from description or name
        extracted = extract_req_ids_from_text(f"{t_name} {t_desc}")
        target_reqs.update(extracted)
        
        test_info = {
            "test_id": t_id,
            "test_name": t_name,
            "status": t_status,
            "description": t_desc
        }
        
        for r_id in target_reqs:
            if r_id not in test_mappings:
                test_mappings[r_id] = []
            test_mappings[r_id].append(test_info)
            
    # Process each requirement
    mapped_tests_list = []
    test_count_list = []
    verification_status_list = []
    failed_test_ids_list = []
    
    for _, req_row in reqs.iterrows():
        r_id = req_row["req_id"]
        tests = test_mappings.get(r_id, [])
        
        test_count_list.append(len(tests))
        
        if not tests:
            verification_status_list.append("UNTESTED")
            mapped_tests_list.append("None")
            failed_test_ids_list.append("")
        else:
            t_names = [f"{t['test_id']} ({t['status']})" for t in tests]
            mapped_tests_list.append("; ".join(t_names))
            
            statuses = [t["status"] for t in tests]
            failed_ids = [t["test_id"] for t in tests if t["status"] == "FAILED"]
            failed_test_ids_list.append(", ".join(failed_ids))
            
            if "FAILED" in statuses:
                verification_status_list.append("VERIFIED_FAIL")
            elif "IN_PROGRESS" in statuses:
                verification_status_list.append("IN_PROGRESS")
            elif all(s == "PASSED" for s in statuses):
                verification_status_list.append("VERIFIED_PASS")
            else:
                verification_status_list.append("UNTESTED")
                
    reqs["test_count"] = test_count_list
    reqs["mapped_tests"] = mapped_tests_list
    reqs["verification_status"] = verification_status_list
    reqs["failed_test_ids"] = failed_test_ids_list
    
    return reqs

def calculate_coverage_metrics(trace_df: pd.DataFrame) -> Dict[str, float]:
    """
    Computes summary traceability and coverage metrics.
    """
    total = len(trace_df)
    if total == 0:
        return {
            "total_requirements": 0,
            "coverage_pct": 0.0,
            "pass_rate_pct": 0.0,
            "untested_count": 0,
            "failed_count": 0,
            "passed_count": 0,
            "in_progress_count": 0
        }
    
    passed = len(trace_df[trace_df["verification_status"] == "VERIFIED_PASS"])
    failed = len(trace_df[trace_df["verification_status"] == "VERIFIED_FAIL"])
    in_progress = len(trace_df[trace_df["verification_status"] == "IN_PROGRESS"])
    untested = len(trace_df[trace_df["verification_status"] == "UNTESTED"])
    
    tested_count = total - untested
    coverage_pct = round((tested_count / total) * 100.0, 1)
    pass_rate_pct = round((passed / total) * 100.0, 1)
    
    return {
        "total_requirements": total,
        "coverage_pct": coverage_pct,
        "pass_rate_pct": pass_rate_pct,
        "untested_count": untested,
        "failed_count": failed,
        "passed_count": passed,
        "in_progress_count": in_progress
    }
