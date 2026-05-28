# Breathe ESG - Data Pipeline & REST API (Backend)

## Overview
This is the backend engine for the Breathe ESG platform. Built with Django and Django Rest Framework (DRF), it handles the ingestion, normalization, and auditing of disparate data sources (SAP, Utility Portals, Corporate Travel APIs) into standardized ESG metrics (Scope 1, 2, and 3).

**Live Deployment:** [https://breathe-esg-backend-gct8.onrender.com]

## Architectural Documentation
The core engineering philosophy, data models, and tradeoffs are documented extensively in the repository. Please review the following files:
* [MODEL.md](./MODEL.md) - Explains the ELT approach, multi-tenancy, and immutable source-of-truth.
* [DECISIONS.md](./DECISIONS.md) - Details decoupled architecture, deterministic flagging, and API-first ingestion.
* [SOURCES.md](./SOURCES.md) - Explains the real-world constraints of SAP, Utility, and Travel data handling.
* [TRADEOFFS.md](./TRADEOFFS.md) - Outlines future scalability improvements (e.g., PostgreSQL, RBAC).

## Core API Endpoints
* `POST /api/upload/sap/` - Ingests SAP fuel/procurement data (Scope 1).
* `POST /api/upload/utility/` - Ingests Utility portal data (Scope 2).
* `POST /api/upload/travel/` - Ingests Corporate travel data (Scope 3).
* `GET /api/dashboard/` - Serves normalized `ActivityRecord` data for the frontend.
* `PATCH /api/approve/<id>/` - Updates record status to `APPROVED`.
* `PATCH /api/fix/<id>/` - Corrects anomaly values and updates status.

## Tech Stack
* **Framework:** Python, Django, Django REST Framework
* **Database:** SQLite (Prototype) / PostgreSQL (Production)
* **Server:** Gunicorn
* **Deployment:** Render

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone <your-backend-repo-url>
   cd breathe-esg-backend

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Run migrations and start the server:**
   ```bash
   python manage.py migrate
   python manage.py runserver

The API will be available at http://127.0.0.1:8000.


