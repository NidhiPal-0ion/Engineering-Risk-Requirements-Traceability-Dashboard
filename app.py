import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

from src.data_loader import (
    load_requirements_csv,
    load_test_matrix_csv,
    get_default_sample_data
)
from src.traceability_engine import (
    build_traceability_matrix,
    calculate_coverage_metrics
)
from src.risk_engine import (
    apply_risk_scoring,
    SEVERITY_WEIGHTS,
    SUBSYSTEM_WEIGHTS,
    VERIFICATION_MULTIPLIERS,
    MAX_RAW_RISK_SCORE
)

# Page Configuration
st.set_page_config(
    page_title="TraceWise | Engineering Risk & Traceability Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Engineering Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .status-badge-fail {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    .status-badge-untested {
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    .status-badge-pass {
        background-color: #D1FAE5;
        color: #065F46;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">TraceWise ⚙️ Engineering Risk & Requirements Traceability</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Wind-Turbine Blade Structural Design Process — Automated Requirements Verification & Risk Matrix Audit</div>', unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Sidebar Data Controls & Filters
    # ---------------------------------------------------------
    st.sidebar.title("🛠️ Configuration & Data")
    
    data_source = st.sidebar.radio(
        "Data Source",
        ["Default Synthetic Dataset (Wind-Turbine Blade)", "Upload Custom CSV Files"]
    )
    
    req_df = pd.DataFrame()
    test_df = pd.DataFrame()
    load_error = None
    
    if data_source == "Default Synthetic Dataset (Wind-Turbine Blade)":
        req_df, test_df = get_default_sample_data()
        st.sidebar.success("Loaded default Wind-Turbine Blade dataset (12 Reqs, 8 Test Cases).")
    else:
        st.sidebar.markdown("### Upload Requirements CSV")
        req_file = st.sidebar.file_uploader("Requirements CSV (req_id, description, subsystem, severity)", type=["csv"], key="req_up")
        
        st.sidebar.markdown("### Upload Test Matrix CSV")
        test_file = st.sidebar.file_uploader("Test Matrix CSV (test_id, test_name, status, req_id/description)", type=["csv"], key="test_up")
        
        if req_file is not None and test_file is not None:
            r_df, r_err = load_requirements_csv(req_file)
            t_df, t_err = load_test_matrix_csv(test_file)
            
            if r_err:
                st.sidebar.error(r_err)
                load_error = r_err
            elif t_err:
                st.sidebar.error(t_err)
                load_error = t_err
            else:
                req_df = r_df
                test_df = t_df
                st.sidebar.success(f"Custom datasets loaded: {len(req_df)} Reqs, {len(test_df)} Tests.")
        else:
            st.sidebar.info("Please upload both Requirements and Test Matrix CSV files.")
            
    if req_df.empty or test_df.empty or load_error:
        st.info("👈 Please select or upload a valid dataset in the sidebar to begin analysis.")
        
        with st.expander("ℹ️ Sample CSV Format Guide"):
            st.markdown("""
            **Requirements CSV Columns:**
            - `req_id`: Unique Requirement ID (e.g. `REQ-BLD-001`)
            - `description`: Text requirement statement
            - `subsystem`: Subsystem category (e.g. `Spar Cap`, `Root Joint`)
            - `severity`: `High`, `Medium`, or `Low`
            
            **Test Matrix CSV Columns:**
            - `test_id`: Unique Test ID (e.g. `TEST-BLD-101`)
            - `test_name`: Name or procedure title
            - `status`: `PASSED`, `FAILED`, `IN_PROGRESS`, or `NOT_STARTED`
            - `req_id` (optional): Explicit target requirement ID, or include in description
            """)
        return
        
    # Build traceability and compute risk scores
    raw_trace_df = build_traceability_matrix(req_df, test_df)
    full_df = apply_risk_scoring(raw_trace_df)
    
    # Sidebar Filters
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 Filter Dashboard")
    
    all_subsystems = sorted(full_df["subsystem"].unique().tolist())
    selected_subsystems = st.sidebar.multiselect("Subsystems", options=all_subsystems, default=all_subsystems)
    
    all_risk_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    selected_risk_levels = st.sidebar.multiselect("Risk Priority Level", options=all_risk_levels, default=all_risk_levels)
    
    all_statuses = ["VERIFIED_PASS", "VERIFIED_FAIL", "UNTESTED", "IN_PROGRESS"]
    selected_statuses = st.sidebar.multiselect("Verification Status", options=all_statuses, default=all_statuses)
    
    search_query = st.sidebar.text_input("Search Req ID / Text", "")
    
    # Filter Execution
    filtered_df = full_df[
        (full_df["subsystem"].isin(selected_subsystems)) &
        (full_df["risk_level"].isin(selected_risk_levels)) &
        (full_df["verification_status"].isin(selected_statuses))
    ]
    
    if search_query:
        sq = search_query.upper().strip()
        filtered_df = filtered_df[
            (filtered_df["req_id"].str.contains(sq)) |
            (filtered_df["description"].str.upper().str.contains(sq)) |
            (filtered_df["subsystem"].str.upper().str.contains(sq))
        ]
        
    # ---------------------------------------------------------
    # KPI Summary Metric Cards
    # ---------------------------------------------------------
    metrics = calculate_coverage_metrics(filtered_df)
    high_risk_untested = len(filtered_df[
        (filtered_df["verification_status"] == "UNTESTED") &
        (filtered_df["risk_level"].isin(["CRITICAL", "HIGH"]))
    ])
    avg_risk_score = round(filtered_df["risk_score"].mean(), 1) if not filtered_df.empty else 0.0
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Requirements", metrics["total_requirements"])
    c2.metric("Verification Coverage", f"{metrics['coverage_pct']}%")
    c3.metric("Failed Verification Tests", metrics["failed_count"])
    c4.metric("High-Risk Untested Gaps", high_risk_untested, delta_color="inverse")
    c5.metric("Avg System Risk Score", f"{avg_risk_score} / 100")
    
    st.markdown("---")
    
    # ---------------------------------------------------------
    # Dedicated Section: Urgent Verification Gaps & Priorities
    # ---------------------------------------------------------
    st.markdown("### 🚨 Urgent Verification Gaps & High-Risk Priorities")
    
    urgent_gaps = filtered_df[
        (filtered_df["risk_level"].isin(["CRITICAL", "HIGH"])) &
        (filtered_df["verification_status"].isin(["UNTESTED", "VERIFIED_FAIL"]))
    ].sort_values(by="risk_score", ascending=False)
    
    if urgent_gaps.empty:
        st.success("✅ No critical or high-risk verification gaps detected in current selection!")
    else:
        st.warning(f"Found **{len(urgent_gaps)}** high-priority requirement gaps that require immediate engineering attention:")
        
        display_urgent = urgent_gaps[[
            "req_id", "subsystem", "severity", "verification_status", "risk_score", "risk_level", "recommended_action"
        ]].copy()
        
        display_urgent.columns = [
            "Req ID", "Subsystem", "Severity", "Verification Status", "Risk Score", "Risk Level", "Recommended Next Action"
        ]
        
        st.dataframe(
            display_urgent,
            use_container_width=True,
            hide_index=True
        )
        
    st.markdown("---")
    
    # ---------------------------------------------------------
    # Visual Analytics Tabs
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Traceability & Subsystems",
        "⚡ Risk Matrix & Distribution",
        "📋 Full Requirement Ledger",
        "📘 Risk Methodology & Help"
    ])
    
    with tab1:
        st.markdown("#### System Verification Status & Coverage Breakdown")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Stacked Bar Chart: Subsystem vs Verification Status
            sub_status = filtered_df.groupby(["subsystem", "verification_status"]).size().reset_index(name="count")
            fig_sub = px.bar(
                sub_status,
                x="subsystem",
                y="count",
                color="verification_status",
                title="Verification Status by Wind-Turbine Subsystem",
                color_discrete_map={
                    "VERIFIED_PASS": "#10B981",
                    "VERIFIED_FAIL": "#EF4444",
                    "IN_PROGRESS": "#3B82F6",
                    "UNTESTED": "#F59E0B"
                },
                labels={"count": "Number of Requirements", "subsystem": "Subsystem", "verification_status": "Status"}
            )
            fig_sub.update_layout(barmode="stack", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_sub, use_container_width=True)
            
        with col_chart2:
            # Donut Chart: Overall System Compliance Distribution
            status_counts = filtered_df["verification_status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Count",
                title="System Compliance Distribution",
                hole=0.4,
                color="Status",
                color_discrete_map={
                    "VERIFIED_PASS": "#10B981",
                    "VERIFIED_FAIL": "#EF4444",
                    "IN_PROGRESS": "#3B82F6",
                    "UNTESTED": "#F59E0B"
                }
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
            
    with tab2:
        st.markdown("#### Risk Priority Matrix")
        
        col_risk1, col_risk2 = st.columns(2)
        
        with col_risk1:
            # Scatter Plot: Subsystem vs Risk Score
            fig_scatter = px.scatter(
                filtered_df,
                x="subsystem",
                y="risk_score",
                color="risk_level",
                size="risk_score",
                hover_data=["req_id", "severity", "verification_status"],
                title="Risk Priority Distribution by Subsystem",
                color_discrete_map={
                    "CRITICAL": "#DC2626",
                    "HIGH": "#EA580C",
                    "MEDIUM": "#D97706",
                    "LOW": "#059669"
                },
                labels={"risk_score": "Risk Score (0-100)", "subsystem": "Subsystem"}
            )
            fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_risk2:
            # Bar Chart: Top Highest Risk Requirements
            top_risk = filtered_df.head(10)
            fig_top = px.bar(
                top_risk,
                x="risk_score",
                y="req_id",
                orientation="h",
                color="risk_level",
                title="Top 10 High-Risk Requirements",
                color_discrete_map={
                    "CRITICAL": "#DC2626",
                    "HIGH": "#EA580C",
                    "MEDIUM": "#D97706",
                    "LOW": "#059669"
                },
                hover_data=["subsystem", "verification_status", "recommended_action"]
            )
            fig_top.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_top, use_container_width=True)

    with tab3:
        st.markdown("#### Complete Requirements & Verification Traceability Ledger")
        
        df_display = filtered_df[[
            "req_id", "subsystem", "severity", "verification_status",
            "test_count", "mapped_tests", "risk_score", "risk_level", "recommended_action", "description"
        ]].copy()
        
        df_display.columns = [
            "Req ID", "Subsystem", "Severity", "Verification Status",
            "Test Count", "Mapped Tests", "Risk Score", "Risk Level", "Recommended Next Action", "Description"
        ]
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
    with tab4:
        st.markdown("#### 📘 Risk Scoring & Traceability Methodology")
        st.markdown("""
        ### Transparent Rule-Based Engineering Risk Model
        
        TraceWise calculates a deterministic **Risk Priority Score** for each requirement based on three key factors:
        
        $$\\text{Raw Risk Score} = S_{\\text{severity}} \\times W_{\\text{subsystem}} \\times M_{\\text{verification}}$$
        
        $$\\text{Normalized Risk Score} = \\min\\left(100, \\text{round}\\left(\\frac{\\text{Raw Risk Score}}{11.25} \\times 100, 1\\right)\\right)$$
        
        ---
        
        #### 1. Base Severity Weight ($S$)
        - **HIGH**: `3.0` (Safety-critical or primary structural failure mode)
        - **MEDIUM**: `2.0` (Operational margin or functional requirement)
        - **LOW**: `1.0` (Non-critical cosmetic or minor compliance item)
        
        #### 2. Subsystem Criticality Weight ($W_{\text{sub}}$)
        - **Spar Cap / Root Joint**: `1.5` (Primary load-bearing carbon/glass laminate & hub attachment interface)
        - **Shear Web**: `1.3` (Internal shear web structural integrity)
        - **Lightning Protection System (LPS)**: `1.2` (Catastrophic lightning strike protection)
        - **Aerodynamic Shell**: `1.1` (Tower clearance & blade aerodynamic profile)
        - **Trailing Edge**: `1.0` (Adhesive bond lines & serration performance)
        
        #### 3. Verification Status Multiplier ($M_{\text{ver}}$)
        - **VERIFIED_FAIL**: `2.5` (Physical test conducted and failed — immediate redesign required)
        - **UNTESTED**: `2.0` (Requirement has no mapped test — high uncertainty gap)
        - **IN_PROGRESS**: `1.2` (Testing underway — pending final verification)
        - **VERIFIED_PASS**: `0.5` (Physical test passed — low residual risk)
        
        ---
        
        #### Risk Classification Thresholds
        - **CRITICAL**: Score $\\ge 70$ (Urgent action needed)
        - **HIGH**: Score $\\ge 50$ (Priority verification/redesign)
        - **MEDIUM**: Score $\\ge 30$ (Standard tracking)
        - **LOW**: Score $< 30$ (Low risk baseline)
        """)

    # ---------------------------------------------------------
    # Export & Reporting Section
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📥 Download Engineering Reports")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # Export Traceability Gaps CSV
        gap_df = filtered_df[filtered_df["verification_status"].isin(["UNTESTED", "VERIFIED_FAIL"])]
        csv_gap = gap_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Traceability Gap Report (CSV)",
            data=csv_gap,
            file_name="tracewise_unresolved_gaps_report.csv",
            mime="text/csv"
        )
        
    with col_exp2:
        # Export Full Risk & Verification Summary CSV
        summary_csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Full Risk & Verification Ledger (CSV)",
            data=summary_csv,
            file_name="tracewise_full_engineering_risk_summary.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
