# Data Model Architecture

The data model is explicitly designed to handle multi-tenancy, normalize disparate data units, and preserve an immutable audit trail for rigorous ESG compliance and reporting.

## Core Architectural Philosophy: ELT over ETL
We employ an **ELT (Extract, Load, Transform)** approach rather than traditional ETL. Data from diverse external sources (SAP, Utility APIs, Travel APIs) is first loaded in its exact raw format before being transformed. This ensures that if ESG calculation methodologies change in the future, historical data can be re-processed without re-querying external systems.

---

## 1. Core Hierarchy (Multi-Tenancy)
* **`Tenant`**: Represents a client organization, ensuring strict data isolation across the platform.
* **`Facility`**: Represents a physical location (e.g., factory, office, plant). Maps directly to SAP plant codes or utility service addresses.
  * **Fields:** `id`, `tenant_id` (FK), `name`, `sap_plant_code`, `location`

## 2. Ingestion & Source Tracking (The Ledger)
* **`IngestionRun`**: Tracks every data pipeline execution or manual upload event.
  * **Fields:** `id`, `tenant_id` (FK), `source_type` (SAP, UTILITY, TRAVEL), `uploaded_at`, `status`
* **`RawRecord` (The Immutable Source of Truth)**: Stores the exact ingested payload before any normalization occurs. 
  * **Fields:** `id`, `ingestion_run_id` (FK), `raw_data` (JSON)
  * *Design Choice:* This table is strictly append-only. It acts as a permanent audit ledger to resolve any data disputes with third-party vendors.

## 3. Normalization & Scope Categorization
* **`ActivityRecord`**: The standardized, normalized data surfaced to the data analyst on the dashboard.
  * **Fields:** `id`, `tenant_id` (FK), `facility_id` (FK), `raw_record_id` (FK - 1:1), `activity_type` (e.g., FUEL_DIESEL, ELECTRICITY_GRID, FLIGHT), `quantity` (Decimal), `unit`, `scope` (1, 2, or 3), `review_status` (PENDING, FLAGGED, APPROVED).
  * **Scope Mapping Logic:**
    * **Scope 1 (Direct):** SAP Data (Fuel/Diesel consumption at owned facilities).
    * **Scope 2 (Indirect):** Utility API (Purchased electricity).
    * **Scope 3 (Value Chain):** Corporate Travel API (Employee flights).
  * *Design Choice:* We use `Decimal` instead of `Float` for `quantity` to prevent floating-point precision loss, which is critical for compliance reporting. 
  * *Design Choice:* Source-specific nuances (like `meter_id` or `flight_cabin`) are stored in a flexible `metadata` JSON field rather than cluttering the schema with sparse columns.

## 4. Audit Trail & Compliance
* **`AuditLog`**: An append-only table tracking state changes of an `ActivityRecord`.
  * **Fields:** `id`, `activity_record_id` (FK), `action` (e.g., VALUE_UPDATED, STATUS_APPROVED), `old_value` (JSON), `new_value` (JSON), `timestamp`
  * *Design Choice:* When a flagged record is corrected (e.g., fixing a 0km flight distance), the original value is preserved here to ensure full human accountability.