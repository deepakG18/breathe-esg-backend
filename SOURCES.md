# Real-World Source Handling & Constraints

## 1. SAP (Fuel and Procurement)
* **Real-World Format:** Sustainability teams typically extract fuel data using standard transaction codes like MB51 (Material Documents for consumption, Movement Type 261) or ME2N (Purchasing).
* **Ingestion Mechanism Chosen:** Flat CSV Upload. Direct API/IDoc integration requires BASIS team approvals and weeks of security reviews, which is unrealistic for initial onboarding.
* **Handled Subset:** Liquid fuels (Diesel, Petrol).
* **What would break in production:** Without a tenant-specific lookup table, internal plant codes (e.g., '1001') are meaningless and cannot be mapped to a physical facility.

## 2. Utility Data (Electricity)
* **Real-World Format:** Exported CSVs from utility portals (similar to Green Button standard).
* **Ingestion Mechanism Chosen:** CSV Upload. PDF parsing is highly brittle across hundreds of different utility providers.
* **Handled Subset:** Active Energy (kWh / MWh) and billing periods.
* **What would break in production:** Billing cycles rarely align with calendar months (e.g., Feb 14 - Mar 13). The system must prorate daily averages to allocate consumption into strict reporting months.

## 3. Corporate Travel (e.g., Concur / Navan)
* **Real-World Format:** Nested JSON exports containing distinct segments (Flights, Hotels, Ground).
* **Ingestion Mechanism Chosen:** JSON Upload. Flattening nested trip itineraries into a single CSV row causes severe data loss.
* **Handled Subset:** Flights (Origin/Destination IATA codes and Cabin Class).
* **What would break in production:** APIs provide airport codes, not distances. The system requires a great-circle (Haversine) calculation against an airport coordinate database to derive trackable distance, combined with DEFRA cabin-class multipliers.