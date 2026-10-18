# Decisions Log

## 2025-10-15 — Data model
- Decision: One row per firm-per-network-observation (not one row per firm).
  "First connection" is derived in analysis, not at data entry.
- Rationale: A firm may appear in multiple networks at different dates;
  collapsing early loses information and hard-codes a definition we may revise.

## 2025-10-15 — IETF Source 1 complete
- Extracted 9 orgs from JvNCnet "new on-line members" section, Oct 1992 IMR.
- Parser challenges: page breaks (form feed \x0c), running footers, and
  "S. C. Johnson" matching the section-marker regex. Documented in code.
- Date handling: used reporting month from header; parenthetical override
  (e.g., Trenton "Sept. 1992") takes precedence over the header month.
- Open question: include non-firms (school district, training institutes)?
- Noted likely typo: "KMPG" -> "KPMG" (not altered in data; flagged in notes).

## 2025-10-16 — IETF Source 1 complete
- Extracted 9 orgs from the JvNCnet "new on-line members (fully operational
  October 1992)" section of the October 1992 Internet Monthly Report.
- Parser challenges solved: page breaks (form feed \x0c), running footers
  ("Cooper... [Page N]"), and company initials like "S. C. Johnson" falsely
  matching the section-marker regex. See code comments in clean_ietf.py.
- Date logic: default to the reporting month from the header; a parenthetical
  override (e.g., Trenton "Sept. 1992") takes precedence.
- Data model: kept rows faithful to source; interpretation added via notes.
- Flagged: "KMPG" likely a typo for "KPMG" (not altered in data).
- Open question for supervisors: should non-firms (school districts, training
  institutes) be included, or only private companies? Source lists them together.