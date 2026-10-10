# TraceWise — Engineering Risk & Requirements Traceability Dashboard ⚙️

> **Systems Engineering & Verification Audit Tool tailored for Wind-Turbine Blade Structural Design**

TraceWise is an interactive, rule-based engineering compliance and requirements traceability dashboard built in Python and Streamlit. It bridges the gap between high-level structural design requirements and physical hardware verification test execution, automatically identifying compliance gaps, unmapped requirements, and test failures while prioritizing engineering risk.

---

## 🌟 Key Features

1. **Requirements & Test Matrix Ingestion**: Load engineering requirements and verification test execution matrices from CSV files with automatic schema validation.
2. **Regex & Relational Traceability Engine**: Uses regex pattern matching (`REQ-[A-Z0-9-]+`) and relational cross-referencing to dynamically link test plans and results to system requirements.
3. **Transparent Rule-Based Engineering Risk Scoring**: Quantitative risk priority calculation factoring requirement severity, subsystem criticality (e.g. Spar Cap vs Trailing Edge), and physical test verification status.
4. **Urgent Verification Gap Highlighting**: A dedicated dashboard section that surfaces high-risk requirements that are currently **untested** or **failed verification**.
5. **Interactive Visual Analytics**: Built-in Plotly charts including subsystem verification breakdown (stacked bar charts), compliance status distribution (donut chart), and risk priority scatter plots.
6. **Actionable Engineering Recommendations**: Auto-generates targeted next actions (e.g., *"URGENT REDESIGN"*, *"URGENT TEST MAPPING"*, *"MONITOR"*) for every requirement.
7. **Exportable Compliance Reports**: Export CSV reports of unresolved traceability gaps and complete executive risk ledgers.

---

## 🔬 Wind-Turbine Blade Engineering Context

TraceWise is pre-loaded with a realistic synthetic engineering dataset for a **Wind-Turbine Blade Subsystem** (relevant to structural design processes at Siemens Gamesa and aerospace/wind energy manufacturers):

- **Spar Cap**: Primary load-bearing structural carbon/glass laminate (Flapwise bending strain & compression buckling).
- **Root Joint**: Critical T-bolt bolted interface securing blade to rotor hub (Fatigue life under cyclic loads).
- **Shear Web**: Internal structural webs resisting transverse shear loads.
- **Lightning Protection System (LPS)**: High-voltage down-conductors and root receptors (IEC 61400-24 compliance).
- **Aerodynamic Shell**: Suction & pressure side laminate profiles (Tip deflection vs tower clearance).
- **Trailing Edge**: Structural bond lines and acoustic noise reduction serrations.

---

## 📐 Risk Scoring Methodology

TraceWise uses a deterministic, fully transparent rule-based risk model to quantify engineering risk without black-box ML models:

$$\text{Raw Risk Score} = S_{\text{severity}} \times W_{\text{subsystem}} \times M_{\text{verification}}$$

$$\text{Normalized Risk Score} = \min\left(100, \text{round}\left(\frac{\text{Raw Risk Score}}{11.25} \times 100, 1\right)\right)$$

### 1. Severity Weight ($S$)
- **HIGH** (`3.0`): Primary structural failure mode, safety-critical requirement.
- **MEDIUM** (`2.0`): Functional margin or standard design operational parameter.
- **LOW** (`1.0`): Non-critical cosmetic or minor operational item.

### 2. Subsystem Criticality Weight ($W_{\text{sub}}$)
- **Spar Cap** / **Root Joint** (`1.5`): High-consequence structural primary components.
- **Shear Web** (`1.3`): Internal structural shear members.
- **Lightning Protection System (LPS)** (`1.2`): High-voltage strike protection.
- **Aerodynamic Shell** (`1.1`): Structural profile & tower clearance limits.
- **Trailing Edge** (`1.0`): Secondary structural bond line & noise serrations.

### 3. Verification Status Multiplier ($M_{\text{ver}}$)
- **VERIFIED_FAIL** (`2.5`): Test executed and failed — urgent redesign or structural review required.
- **UNTESTED** (`2.0`): Requirement lacks mapped test plan — high uncertainty gap.
- **IN_PROGRESS** (`1.2`): Verification testing underway in lab.
- **VERIFIED_PASS** (`0.5`): Verification complete and passed — low residual risk.

### Risk Level Classification
- 🔴 **CRITICAL**: Score $\ge 70.0$
- 🟠 **HIGH**: Score $\ge 50.0$
- 🟡 **MEDIUM**: Score $\ge 30.0$
- 🟢 **LOW**: Score $< 30.0$

---

## 🛠️ Repository Architecture & Code Reuse Attribution

This project is inspired by and builds upon the foundational requirements mapping concepts from:
- Reference Project: [requirements-traceability-engine](https://github.com/mzaib1012/requirements-traceability-engine) (MIT License).

### Distinction of Reused vs. Newly Implemented Features

| Feature / Component | Source | Implementation Notes |
| :--- | :--- | :--- |
| **Regex ID Parsing (`REQ-XXX`)** | Reused & Adapted | Adapted from reference engine regex concepts to extract requirement handles from free text. |
| **Relational Verification Merge** | Reused & Adapted | Extended relational merge logic to support explicit and implicit multi-requirement mappings. |
| **Interactive Streamlit Dashboard** | Newly Implemented | Developed interactive web UI with sidebar filter controls and custom KPI metric cards. |
| **Rule-Based Risk Model** | Newly Implemented | Formulated transparent severity-subsystem-status multiplication scoring engine. |
| **Urgent Gap Highlighting Section** | Newly Implemented | Added dedicated priority alert callout section targeting high-risk untested/failed requirements. |
| **Actionable Recommendations** | Newly Implemented | Automated engineering next step recommendations for each status/severity pair. |
| **Plotly Analytics & Data Export** | Newly Implemented | Created stacked bar charts, scatter risk distribution charts, and CSV report export. |
| **Pytest Automated Test Suite** | Newly Implemented | Comprehensive unit tests for data loader, traceability engine, and risk scoring. |

```
Engineering-Risk-Requirements-Traceability-Dashboard/
├── app.py                      # Main Streamlit Dashboard Application
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # CSV Ingestion, Validation & Sample Data Provider
│   ├── traceability_engine.py  # Regex Parsing, Traceability Matrix & Coverage Metrics
│   └── risk_engine.py          # Rule-Based Risk Scoring & Recommendation Engine
├── data/
│   ├── sample_requirements.csv # Wind-Turbine Blade Requirements Dataset
│   └── sample_test_matrix.csv  # Verification Test Matrix Execution Log
├── tests/
│   ├── test_data_loader.py     # Unit Tests for CSV Validation & Sample Ingestion
│   ├── test_traceability.py    # Unit Tests for Regex Extraction & Traceability Matrix
│   └── test_risk.py            # Unit Tests for Risk Formula & Action Recommendations
├── .github/workflows/ci.yml    # GitHub Actions Continuous Integration Workflow
├── requirements.txt            # Dependency Requirements
├── README.md                   # Project Documentation
└── .gitignore                  # Git Ignore Specifications
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.10+ installed

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*

### 3. Run Automated Tests
```bash
pytest
```

---

## 📊 Sample Visualizations Guide

1. **Dashboard KPI Bar**: Instant executive overview of Total Requirements, Coverage %, Failed Test Count, and High-Risk Untested Gaps.
2. **Urgent Verification Gaps**: Highlighted callout table showing critical unverified requirements requiring immediate action.
3. **Traceability & Subsystems Tab**: Visualizes verification coverage breakdown by subsystem using Plotly stacked bar charts.
4. **Risk Matrix & Distribution Tab**: Displays top high-risk requirements and risk scatter plot across subsystems.

---

## ⚖️ Limitations & Future Enhancements

- **Static Rule-Based Weights**: Subsystem weights are currently static; future iterations could support customizable weight sliders in the UI.
- **Single Level Traceability**: Direct mapping between Level-1 Requirements and Test Cases; nested hierarchical requirements breakdown (Level 1 -> Level 2 -> Test) can be added in future versions.

---

## 📜 License & Attribution

Distributed under the MIT License. Reused and adapted components maintain attribution to [mzaib1012/requirements-traceability-engine](https://github.com/mzaib1012/requirements-traceability-engine).
