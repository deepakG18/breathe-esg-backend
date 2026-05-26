# Architectural & Engineering Decisions

## Decision 1: Decoupled Architecture (Django API + React UI)
* **What I decided:** I built a decoupled system using Django Rest Framework (DRF) for the backend and React (Vite) for the frontend, deploying them independently on Render and Vercel.
* **Why I chose this (Engineering Trade-off):** ESG platforms often evolve into complex, data-heavy dashboards requiring rich interactivity. React provides robust state management for dynamic UI filtering, while DRF acts as a reliable, stateless API. Deploying them separately leverages Vercel's Edge Network for the UI and Render's backend compute, mimicking modern enterprise architectures better than traditional monolithic server-rendered templates.
* **What I would ask the PM:** As the application scales, will we need to expose our REST APIs to third-party integrations (like a client's internal dashboard)? If so, we need to prioritize API rate limiting and API key management.

## Decision 2: The "Source of Truth" & Audit Trail Approach
* **What I decided:** I implemented an immutable `RawRecord` table to store the exact JSON payload of the uploaded data, alongside an `ActivityRecord` table for the normalized data.
* **Why I chose this (Engineering Trade-off):** The assignment strictly requires "source-of-truth tracking." If we overwrite the original uploaded data during normalization (e.g., unit conversion), we destroy the audit trail. By separating the raw ingested row from the processed row, auditors can always verify exactly what the client's system submitted versus how our system interpreted it.
* **What I would ask the PM:** If a user edits a flagged row, do we want to keep a full version history of the normalized row, or just an append-only `AuditLog` of the changes applied to it?

## Decision 3: Multi-Tenancy Strategy
* **What I decided:** I used a shared-database, shared-schema approach with a strict `tenant_id` foreign key on every operational table.
* **Why I chose this (Engineering Trade-off):** Implementing a completely isolated physical database per tenant is massive over-engineering for a prototype. A row-level `tenant_id` is standard industry practice for B2B SaaS MVPs. It ensures data isolation without the overhead of complex database migrations and scaling costs.
* **What I would ask the PM:** Do we foresee enterprise clients (e.g., banks or government bodies) requiring completely isolated physical databases for compliance/legal reasons in the near future?

## Decision 4: Deterministic Data Flagging vs. Hard Rejection
* **What I decided:** Instead of rejecting bad API payloads (e.g., a flight with `0` distance), the backend saves the record but forces its `review_status` to `FLAGGED`.
* **Why I chose this (Engineering Trade-off):** In enterprise integrations, failing an entire batch upload because of one malformed row creates immense friction. By accepting the data but quarantining it with a `FLAGGED` status, we maintain a smooth ingestion pipeline while forcing human intervention (Data Analyst) to correct the anomaly before it enters Scope calculations.
* **What I would ask the PM:** Should we implement an "Auto-Reject" threshold? For example, if a batch contains more than 50% flagged records, should we reject the whole batch and alert the vendor?

## Decision 5: API-First Ingestion Mechanism (Simulating Real-World Systems)
* **What I decided:** Rather than building manual CSV uploaders or brittle PDF OCR parsers, I built REST API endpoints (`/api/upload/sap/`, `/api/upload/travel/`) that accept structured JSON payloads.
* **Why I chose this (Engineering Trade-off):** Real-world ESG platforms are moving towards automated system-to-system integrations. Travel platforms (Navan, Concur) and modern Utility gateways provide JSON APIs. For SAP (which is traditionally CSV/Flat File), exposing a JSON endpoint allows middleware (like MuleSoft or SAP PI) to push data to us seamlessly. This proves the system is API-ready.
* **What I would ask the PM:** For legacy clients who absolutely cannot use APIs, should we build a generic CSV mapper UI, or provide them with a strict Excel template that they must follow?