# Data Model Architecture

The data model is explicitly designed to handle multi-tenancy, normalize disparate units, and preserve an immutable audit trail for ESG reporting.

## 1. Core Hierarchy
* **`Tenant`**: Represents a client organization.
* **`Facility`**: Represents a physical location (factory, office). Maps to SAP plant codes or utility service addresses.
  * Fields: `id`, `tenant_id` (FK), `name`, `sap_plant_code`, `location`

## 2. Ingestion & Source Tracking
* **`IngestionRun`**: Tracks every data upload event.
  * Fields: `id`, `tenant_id` (FK), `source_type` (SAP, UTILITY, TRAVEL), `uploaded_by`, `uploaded_at`, `status`
* **`RawRecord`**: **(The Immutable Source of Truth)** Stores the exact ingested row before any normalization. 
  * Fields: `id`, `ingestion_run_id` (FK), `raw_data` (JSONB)
  * *Design Choice:* Never overwritten. Ensures complete auditability if conversion logic changes.

## 3. Normalization & Review
* **`ActivityRecord`**: The normalized data surfaced to the analyst.
  * Fields: `id`, `tenant_id` (FK), `facility_id` (FK), `raw_record_id` (FK - 1:1), `activity_type` (e.g., FUEL_DIESEL, ELECTRICITY_GRID, FLIGHT), `quantity` (Decimal), `unit`, `period_start`, `period_end`, `scope` (1, 2, or 3), `review_status`
  * `metadata` (JSONB): Captures source-specific data without breaking the schema (e.g., `{"meter_id": "123", "tariff": "HT-1"}` for utility, or `{"origin": "BOM", "cabin": "ECONOMY"}` for travel).
  * *Note:* Uses `Decimal` instead of `Float` to prevent precision loss in audit data.

## 4. Audit Trail
* **`AuditLog`**: Append-only table tracking state changes of an `ActivityRecord`.
  * Fields: `id`, `activity_record_id` (FK), `action`, `changed_by`, `old_value` (JSONB), `new_value` (JSONB), `timestamp`