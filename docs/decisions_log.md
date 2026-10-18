# Decisions Log

## 2026-10-13 — Data model
- Decision: One row per firm-per-network-observation (not one row per firm).
  "First connection" is derived in analysis, not at data entry.
- Rationale: A firm may appear in multiple networks at different dates;
  collapsing early loses information and hard-codes a definition we may revise.

## 2026-10-15 — IETF Source 1 complete
- Extracted 9 orgs from JvNCnet "new on-line members" section, Oct 1992 IMR.
- Parser challenges: page breaks (form feed \x0c), running footers, and
  "S. C. Johnson" matching the section-marker regex. Documented in code.
- Date handling: used reporting month from header; parenthetical override
  (e.g., Trenton "Sept. 1992") takes precedence over the header month.
- Open question: include non-firms (school district, training institutes)?
- Noted likely typo: "KMPG" -> "KPMG" (not altered in data; flagged in notes).

## 2026-10-16 — IETF Source 1 complete
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

## 2026-10-18 — UUCP coverage caveat (IMPORTANT)
- UUCP "first connection" = first appearance in AVAILABLE map snapshots,
  not verified true first connection.
- File coverage by year in encse/uucp-map is highly uneven:
  1987: 418 files, 1988: 1572, 1989: 2, 1990: 3, 1991: 317, 1992: 2389.
- Consequences:
  * 1989-1990 are effectively missing -> firms first connecting then are
    mis-dated to their next appearance (1991/1992), inflating those years.
  * Left-censoring: firms already on UUCP before the first map (Apr 1987)
    all collapse to 1987-04; their true first date is unknown.
- Implication: UUCP year distribution reflects SNAPSHOT AVAILABILITY as much
  as actual adoption. Treat UUCP dates as upper bounds / "observed by" dates.
- Open question for supervisors: acceptable to use "first observed in maps"
  as the measure, with this caveat? Or restrict to well-covered years only?

## 2026-10-18 — UUCP hand-review (25-row sample)
- Of 25 random firm records: ~15 clear companies, ~4 divisions/projects of
  real firms (TRW, Xerox, HP divisions), ~6 non-firms (a high school,
  placeholder text "Not Organized"/"Private use...", likely hobbyist BBSes).
- Estimated ~15-25% false-positive rate in the firm set.
- Added filters: school terms to ACADEMIC_RE; junk/placeholder JUNK_RE.
- Remaining limitations: BBSes hard to distinguish; divisions inflate counts
  and need parent-company consolidation (fuzzy matching) — future work.