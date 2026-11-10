#  Air Quality Monitoring – DataOps & MLOps

##  Project Overview

**Air Quality Monitoring – DataOps & MLOps** is a real-time air quality monitoring platform designed to collect, process, analyze, and monitor environmental data.

The main objective is to detect abnormal air quality conditions using data engineering pipelines and machine learning techniques.

The project integrates DataOps and MLOps practices to ensure reliable data processing, model tracking, and deployment.

##  Project Objectives

- Collect air quality data from IoT sensors or simulated data sources.
- Process real-time data streams.
- Detect abnormal air quality values using Machine Learning.
- Store processed data in a PostgreSQL database.
- Track and manage ML models using MLflow.
- Automate workflows with Apache Airflow.
- Expose prediction services through FastAPI.
- Containerize services using Docker.

##  System Architecture

The proposed architecture follows this pipeline:

```text
IoT Sensors / Python Data Generator
                |
                v
             Apache Kafka
                |
                v
      Apache Spark Streaming
                |
         Data Processing
                |
          +-----+-----+
          |           |
          v           v
      PostgreSQL   Anomaly Detection
                        |
                        v
                   MLflow
                        |
                        v
                    FastAPI
                        |
                        v
                   Dashboard
```

##  Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Apache Kafka | Real-time data streaming |
| Apache Spark | Data processing |
| PostgreSQL | Data storage |
| Apache Airflow | Workflow orchestration |
| MLflow | ML experiment tracking |
| FastAPI | Prediction API |
| Scikit-learn | Machine Learning |
| Docker | Containerization |
| Git & GitHub | Version control and collaboration |

##  Project Structure

```text
Air-Quality-Monitoring/
│
├── data-generator/
│   └── Generate simulated sensor data
│
├── kafka/
│   └── Kafka configuration
│
├── spark/
│   └── Streaming and data processing
│
├── database/
│   └── PostgreSQL configuration
│
├── airflow/
│   └── DAGs and workflow orchestration
│
├── ml/
│   └── Machine Learning models
│
├── mlflow/
│   └── Experiment tracking
│
├── api/
│   └── FastAPI prediction service
│
├── dashboard/
│   └── Monitoring dashboard
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

*Note: This is the proposed structure. Update it to match the actual folders created in the repository.*

##  Data Pipeline

The platform is organized into the following stages:

1. **Data Collection:** Generate or collect air quality measurements.
2. **Data Streaming:** Send raw data to Kafka.
3. **Data Processing:** Use Spark Structured Streaming to process incoming data.
4. **Data Storage:** Save processed measurements in PostgreSQL.
5. **Anomaly Detection:** Apply Machine Learning algorithms to identify abnormal measurements.
6. **Model Management:** Track experiments and models using MLflow.
7. **API Deployment:** Provide predictions through FastAPI.
8. **Monitoring:** Visualize air quality indicators and detected anomalies.

##  Installation and Execution

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Git

### Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Air-Quality-Monitoring
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run with Docker Compose

Once the Docker Compose configuration is ready:

```bash
docker compose up --build -d
```

##  Team Members

This project is developed by a team of three students as part of an academic DataOps & MLOps project.

- Member 1 – Project Coordinator
- Member 2 – Data Engineering
- Member 3 – Machine Learning & MLOps

##  Project Timeline

**Final deadline: December 15, 2026.**

Project planning, development, integration, testing, and documentation are organized using Jira.

##  Project Status

 Currently under development.

##  License

This project is developed for academic and educational purposes.
