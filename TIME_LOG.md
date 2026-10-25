# Time Log

| Date | Phase | Task | Time | Notes / Blockers |
|------|-------|------|------|------------------|
| 2026-10-13 | 0 | Initial project setup attempt | 1h | Created folders; hit conda issues |
| 2026-10-18 | 0 | Install/configure environment | 0.5h | "conda command not found"; resolved by activating env |
| 2026-10-18 | 0 | Debug duplicated project folders | 0.75h | VS Code + terminal pointed at different folders; consolidated 3 copies into one |
| 2026-10-18 | 0 | Recreate docs (README, data dictionary, etc.) | 0.5h | Terminal paste errors with "\|"; learned editor-vs-terminal distinction |
| 2026-10-18 | 0 | Git init + first commit | 0.25h | — |
| 2026-10-18 | 1-2 | Download + inspect IETF Oct 1992 report | 0.5h | Saved raw text manually; studied section/line format |
| 2026-10-18 | 1-2 | Write + debug IETF parser | 1h | Page breaks (form feed \x0c), running footers, and "S. C. Johnson" matching the section-marker regex |
| 2026-10-18 | 1-2 | Finalize + hand-review IETF data | 0.75h | Split name/city/state; dates to YYYY-MM; notes on typos/non-firms |
| 2026-10-18 | 2 | Clone + explore UUCP maps | 0.5h | Studied #N/#O/#P record format; confirmed date comes from filename not #W |
| 2026-10-18 | 2 | Write UUCP parser | 0.75h | Parsed 1,826 files -> 113k records |
| 2026-10-18 | 2 | Filter firms + deduplicate | 0.75h | Removed universities/junk; dedup to earliest appearance -> ~8,200 firms |
| 2026-10-18 | 2 | Hand-review 25-row UUCP sample | 0.5h | Found ~15-25% false positives (schools, BBSes); added filters |
| 2026-10-18 | 3 | Aggregate sources + verify matching | 0.5h | Combined dataset; verified name-normalization logic |
| 2026-10-18 | 3 | Reshape to supervisors' target schema | 0.5h | Mapped to exact example columns + controlled vocab |
| 2026-10-18 | 4 | Analysis: summaries + figures | 0.5h | Found + documented UUCP snapshot-coverage anomaly (1989-90 gap) |
| 2026-10-18 | 5 | Documentation (README, decisions, progress note) | 1h | — |
| 2026-10-18 | 5 | Push to GitHub | 0.5h | Remote URL placeholder + auth token setup |

Approximate total: ~12 hours

| 2026-10-22 | 6 | Data-quality fixes (states, names, junk filter) | 0.25h | |
| 2026-10-22 | 6 | Install + learn LinkTransformer | 0.25h | slow first import |
| 2026-10-22 | 6 | Dedup by state + address validation | 0.25h | |
| 2026-10-22 | 6 | Found/fixed shared-facility confounder | 0.125h | 2 giant address groups polluted stat |
| 2026-10-22 | 6 | Compute + write up dedup statistic | 0.125h | 75.7% full dataset |

| 2026-10-26 | 7 | Source 3 (NSFNET): find sample, build parser | 0.75h | Multi-line addresses, intl countries |
| 2026-10-26 | 7 | Finalize NSFNET + integrate into pipeline | 0.75h | Fixed connectivity_type mapping |