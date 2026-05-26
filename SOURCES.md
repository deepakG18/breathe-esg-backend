# Real-World Source Handling & Constraints

## 1. SAP (Fuel and Procurement)
* **Real-World Format Research:** Traditionally, sustainability teams extract fuel data using transaction codes like MB51 or ME2N (outputting Flat CSVs). However, modern SAP environments (like S/4HANA) increasingly expose data via **OData Services (JSON)**.
* **Ingestion Mechanism Chosen:** REST API (JSON Payload). 
* **Why:** Instead of building a brittle CSV parser, I designed the endpoint (`/api/upload/sap/`) to accept JSON. In a real-world enterprise architecture, a middleware layer (like MuleSoft or SAP PI) would extract the SAP data and push it as a JSON payload to our endpoint.
* **Handled Subset:** Liquid fuels (e.g., Diesel consumption).
* **What would break in production:** Internal SAP plant codes (e.g., '1001') are meaningless on their own. Without a robust tenant-specific lookup table in our database mapping '1001' to "Bhopal Plant 1", the data cannot be attributed to a physical facility.

## 2. Utility Data (Electricity)
* **Real-World Format Research:** Utility data is notoriously fragmented. It comes as PDF bills, portal CSV exports (Green Button standard), or occasionally modern Smart Meter APIs.
* **Ingestion Mechanism Chosen:** REST API (JSON Payload). 
* **Why:** PDF parsing via OCR is highly brittle and unscalable across hundreds of different utility providers. I opted to design a structured JSON endpoint (`/api/upload/utility/`) assuming the client uses an automated utility data aggregator (like Arc or Urjanet) that standardizes the data and pushes it via API.
* **Handled Subset:** Active Energy (kWh) and metered billing periods.
* **What would break in production:** Utility billing cycles rarely align perfectly with calendar months (e.g., a bill spanning Feb 14 - Mar 13). The system currently accepts the raw period, but a production reporting engine would need complex logic to prorate daily averages and allocate consumption strictly into the correct calendar months.

## 3. Corporate Travel (e.g., Concur / Navan)
* **Real-World Format Research:** Modern travel management platforms export highly nested JSON objects containing distinct itinerary segments (Flights, Hotels, Ground Transport).
* **Ingestion Mechanism Chosen:** REST API (JSON Payload).
* **Why:** Forcing a nested trip itinerary into a flat CSV results in severe data loss or messy duplication. A JSON payload perfectly preserves the hierarchical reality of travel data.
* **Handled Subset:** Flights (Origin/Destination IATA codes and Cabin Class).
* **What would break in production:** Travel APIs often provide airport codes, but not the actual flight distances. A production system would require a geographical database to perform great-circle (Haversine) distance calculations between airports, before multiplying that distance by DEFRA/EPA cabin-class emission factors.