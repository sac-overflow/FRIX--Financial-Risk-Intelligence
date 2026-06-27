# Security Policy

## Licensing & Intended Use
FRIX (Financial Risk Intelligence Platform) is an open-source, production-style demonstration of applied machine learning in fintech. While designed with production architecture in mind, it should undergo formal security audits before being deployed to handle live, real-world financial transactions.

## Supported Versions

Only the latest version of the `main` branch is actively supported with security updates. 

| Version | Supported          |
| ------- | ------------------ |
| >= 1.0.0| :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

We take the security of financial risk intelligence seriously. If you discover a security vulnerability within FRIX, please do not open a public GitHub issue. Instead, report it responsibly via the process below:

1. **Email the Maintainers:** Send a detailed report to `sachhithanandm@gmail.com` .
2. **Include Details:** * A description of the vulnerability.
   * Steps to reproduce the issue (proof-of-concept code or API payloads).
   * Potential impact (e.g., model manipulation, data leakage, API denial of service).
3. **Response Timeline:** We acknowledge receipt of vulnerability reports within 48 hours and strive to provide a timeline for remediation within 7 days.

## Core Security Safeguards in FRIX

### 1. Dependency & Container Security
* **Automated Scanning:** We use GitHub Actions CI to validate code stability. (Tip: You can add tools like Snyk or GitHub Dependabot to scan `requirements-api.txt` and `package.json`).
* **Minimal Docker Images:** The FastAPI service uses optimized, non-root base images to minimize the attack surface in containerized environments.

### 2. API & Data Security
* **Input Validation:** Every transaction payload entering the `/predict-fraud` endpoint is strictly validated via Pydantic schemas (`schemas.py`) to prevent injection attacks and malformed data from crashing the inference engine.
* **Environment Isolation:** Secrets, system modes (`FRIX_TEST_MODE`), and backend base URLs (`VITE_FRIX_API_BASE_URL`) are strictly managed via environment variables and `.env` files, which are explicitly ignored by Git.

### 3. Adversarial ML & Model Security
As an AI-driven platform, FRIX acknowledges risks unique to machine learning pipelines:
* **Model Poisoning:** Model artifacts (`random_forest_fraud_model_day2`) should only be loaded from verified, secure storage layers.
* **Inference Exploit Mitigation:** FRIX utilizes a `Reason Code Generator` alongside raw probability scores to ensure transparent risk decisions, making it harder for malicious actors to black-box probe the model without detection.
