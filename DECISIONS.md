# Architectural & Engineering Decisions

## Decision [Number]: [Topic]
* **What I decided:** [Direct statement of the choice]
* **Why I chose this (Engineering Trade-off):** [Technical justification, what alternatives were rejected and why]
* **What I would ask the PM:** [Questions regarding business logic or edge cases]


## Decision 1: The "Source of Truth" & Audit Trail Approach
* **What I decided:** I will implement an immutable RawRecord table to store the exact JSON payload of the uploaded data, alongside an ActivityRecord table for the normalized data.
* **Why I chose this (Engineering Trade-off):** The assignment strictly requires "source-of-truth tracking" and an "audit trail." If we overwrite the original uploaded data during normalization (e.g., unit conversion), we destroy the audit trail. By separating the raw ingested row from the processed row, auditors can always verify exactly what the client submitted versus how the system interpreted it.
* **What I would ask the PM:** If a user edits a row, do we want to keep a full version history of the normalized row, or just an append-only log of changes applied to it?

## Decision 2: Multi-Tenancy Strategy
* **What I decided:** I will use a shared-database, shared-schema approach with a strict tenant_id foreign key on every operational table, enforced at the application (ORM) level.
* **Why I chose this (Engineering Trade-off):** Implementing a completely isolated database per tenant or schema per tenant (like using PostgreSQL schemas) is massive over-engineering for a 4-day prototype. A row-level tenant_id is standard industry practice for B2B SaaS MVPs. It ensures data isolation without the overhead of complex database migrations.
* **What I would ask the PM:** Do we foresee enterprise clients requiring completely isolated physical databases for compliance reasons in the near future?

## Decision 3: SAP Ingestion Mechanism
* **What I decided:** For the SAP source, the application will accept a flat CSV export (simulating an export from transaction MB51 or ME2N) rather than integrating via SAP IDoc or OData API.
* **Why I chose this (Engineering Trade-off):** Realistically, establishing an API connection with an enterprise SAP system requires weeks of security reviews, BASIS team involvement, and network configuration. For onboarding a new client rapidly, a sustainability lead will almost always rely on manual CSV/Excel exports from the ERP system first. This fits the "realistic shape" requirement of the assignment.
* **What I would ask the PM:** Should the system enforce a strict column header validation for the SAP CSV, or should we build a dynamic mapping tool since different SAP instances might have German vs. English headers?

## Decision 4: Utility Data (Electricity) Ingestion Mechanism
* **What I decided:** The system will process CSV exports from utility web portals (similar to the Green Button standard) rather than attempting to parse PDF utility bills or integrating directly with utility APIs.
* **Why I chose this (Engineering Trade-off):** PDF parsing is highly brittle; a regex or OCR pipeline that works for one utility provider will immediately break for another, making it unscalable for a 4-day build. Live APIs are fragmented and require credentials that facilities teams often don't have during initial onboarding. Processing portal CSVs is the most reliable and realistic middle ground. Furthermore, the system is designed to handle "calendarization" (allocating a Feb 14 - Mar 13 bill across two strict calendar months) by calculating daily averages.
* **What I would ask the PM:** How should the system resolve conflicts if a user accidentally uploads a revised utility bill that overlaps with an already approved billing period?

## Decision 5: Corporate Travel Ingestion Mechanism
* **What I decided:** The application will accept nested JSON payloads to mimic data exports from platforms like Concur or Navan, rather than flattened CSVs.
* **Why I chose this (Engineering Trade-off):** Travel itineraries are inherently relational. A single trip often contains multiple flight legs, hotel nights, and ground transport. Forcing this hierarchy into a flat CSV results in severe data loss or messy duplication. A JSON structure preserves the real-world shape of the data. I also decided the backend must accept raw IATA airport codes and compute great-circle (Haversine) distances itself, because raw travel platform exports rarely provide pre-calculated distances.
* **What I would ask the PM:** If a flight segment in the JSON payload is missing the "cabin class" attribute (which significantly changes the emission multiplier), should the system flag it for manual review, or automatically default to an "Average/Economy" emission factor?