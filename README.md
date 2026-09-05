# Sentinel: Cloud-Native DevSecOps Data Pipeline

## Executive Summary
Sentinel is a production-grade, cloud-native data pipeline designed for automated ingestion, processing, and observability of real-time market data. The project leverages a serverless architecture to ensure high availability and scalability while integrating automated security scanning into the CI/CD lifecycle. A core highlight of this project is its resilient design, which successfully migrated from a local-hosted infrastructure to a fully managed cloud ecosystem following a critical local environment failure.

## System Architecture
The pipeline follows a modular architecture to ensure separation of concerns:
1. **Data Ingestion Layer:** A Python-based service interacting with public REST APIs to fetch real-time cryptocurrency metrics.
2. **Storage Layer:** Data is persisted in a serverless PostgreSQL environment (Neon.tech) with encrypted connection strings.
3. **Orchestration & Automation:** GitHub Actions manages the end-to-end lifecycle, from code commit to container building and execution.
4. **Security Layer:** Integrated DevSecOps practices using Aquasecurity Trivy for automated vulnerability scanning.
5. **Observability Layer:** Real-time data visualization and infrastructure monitoring via Grafana Cloud.

## Technical Stack
* **Programming Language:** Python 3.9
* **Database:** PostgreSQL (Neon Serverless)
* **Containerization:** Docker (Optimized Multi-stage builds)
* **CI/CD Platform:** GitHub Actions
* **Security Scanning:** Trivy
* **Monitoring:** Grafana Cloud

## Core DevOps Implementations

### 1. Optimized Containerization
The project utilizes a multi-stage Docker build strategy. This approach separates the build-time dependencies from the runtime environment, resulting in a lightweight production image. This reduces the attack surface and ensures faster deployment cycles in a cloud environment.

### 2. Automated DevSecOps Pipeline
A robust CI/CD pipeline is implemented to enforce security and reliability standards:
* **Automated Builds:** Triggered on every push to the main branch.
* **Vulnerability Assessment:** Trivy scans the Docker image for Critical and High vulnerabilities (CVEs) before execution.
* **Secret Management:** Sensitive credentials, including database connection strings, are managed via GitHub Encrypted Secrets, preventing exposure in the source code.
