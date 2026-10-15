# Decisions Log

## 2025-10-16 — Data model
- Decision: One row per firm-per-network-observation (not one row per firm).
  "First connection" is derived in analysis, not at data entry.
- Rationale: A firm may appear in multiple networks at different dates;
  collapsing early loses information and hard-codes a definition we may revise.
