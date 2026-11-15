# Jira Scrum Management – Air Quality Monitoring (DataOps & MLOps)

This directory contains the complete agile project structure for the **Air Quality Monitoring – Real-Time Anomaly Detection Platform**.

## 1. Project Overview
- **Project Name:** `Air Quality Monitoring – DataOps & MLOps`
- **Project Key:** `KAN`
- **Project Type:** Jira Software (Scrum / Kanban)
- **Scrum Board URL:** [https://ma4873173-1794336439742.atlassian.net/jira/software/projects/KAN/boards/1](https://ma4873173-1794336439742.atlassian.net/jira/software/projects/KAN/boards/1)
- **Board Workflow:** `TO DO` ➔ `IN PROGRESS` ➔ `IN REVIEW` ➔ `DONE`

---

## 2. Team Member Assignments

| Role | Responsibility | Configurable Jira Placeholder | Configurable GitHub Username |
| :--- | :--- | :--- | :--- |
| **Member 1** | Project Manager / Scrum Master / Kafka / Airflow / DevOps | `MEMBER_1_ACCOUNT_ID` | `devops-scrum-lead` |
| **Member 2** | Data Engineer / Python / Spark / PostgreSQL | `MEMBER_2_ACCOUNT_ID` | `data-engineer-lead` |
| **Member 3** | ML Engineer / Scikit-learn / MLflow / FastAPI / Dashboard | `MEMBER_3_ACCOUNT_ID` | `mlops-engineer-lead` |

*Note: Replace placeholders in `.env` with actual Atlassian account IDs.*

---

## 3. Sprint Calendar & Timeline

| Sprint | Dates | Focus & Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Sprint 1** | Nov 10 – Nov 16 | Project Setup, IoT Simulator, Docker & Kafka Topics | **Done / Finalizing** |
| **Sprint 2** | Nov 17 – Nov 23 | Spark Streaming, Data Cleaning, PostgreSQL & Airflow DAGs | **In Progress** |
| **Sprint 3** | Nov 24 – Nov 30 | Machine Learning, Model Comparison, MLflow Tracking & Registry | **Planned** |
| **Sprint 4** | Dec 01 – Dec 07 | FastAPI Prediction Endpoints, Interactive Streamlit Dashboard | **Planned** |
| **Sprint 5** | Dec 08 – Dec 15 | Testing, Deployment Validation, LaTeX Technical Report, Slides & Demo | **Planned** |

**Current Date:** 15 November 2026  
**Final Project Deadline:** 15 December 2026 (30 calendar days remaining)

---

## 4. How to Import into Jira

### Option A: 1-Click CSV Import
1. Navigate to your Jira Cloud / Server instance.
2. Go to **Settings (Gear Icon)** ➔ **System** ➔ **External System Import**.
3. Choose **CSV** and select [`jira_backlog.csv`](file:///c:/Users/Pc/Desktop/data-ops/jira/jira_backlog.csv).
4. Map the fields (Issue Type, Summary, Description, Priority, Assignee, Story Points, Sprint, Parent Id).
5. Click **Import**.

### Option B: Automated REST API Script
1. Set `JIRA_INSTANCE_URL`, `JIRA_USER_EMAIL`, and `JIRA_API_TOKEN` in `.env`.
2. Run:
   ```bash
   python jira/jira_setup_script.py
   ```
