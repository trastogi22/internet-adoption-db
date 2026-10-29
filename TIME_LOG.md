# Time Log

| Date | Phase | Task | Time | Notes / Blockers |
|------|-------|------|------|------------------|
| 2026-10-13 | 0 | Initial project setup attempt | 1h | Created folders; hit conda issues |
| 2026-10-18 | 0 | Install/configure environment | 0.5h | "conda command not found"; resolved by activating env |
| 2026-10-18 | 0 | Debug duplicated project folders | 0.75h | VS Code + terminal pointed at different folders; consolidated 3 copies into one |
| 2026-10-18 | 0 | Recreate docs (README, data dictionary, etc.) | 0.5h | Terminal paste errors with pipe char; learned editor-vs-terminal distinction |
| 2026-10-18 | 0 | Git init + first commit | 0.25h | — |
| 2026-10-18 | 1-2 | Download + inspect IETF Oct 1992 report | 0.5h | Saved raw text manually; studied section/line format |
| 2026-10-18 | 1-2 | Write + debug IETF parser | 1h | Page breaks (form feed), running footers, "S. C. Johnson" matching section-marker regex |
| 2026-10-18 | 1-2 | Finalize + hand-review IETF data | 0.75h | Split name/city/state; dates to YYYY-MM; notes on typos/non-firms |
| 2026-10-18 | 2 | Clone + explore UUCP maps | 0.5h | Studied #N/#O/#P format; date from filename not #W |
| 2026-10-18 | 2 | Write UUCP parser | 0.75h | Parsed 1,826 files -> 113k records |
| 2026-10-18 | 2 | Filter firms + deduplicate | 0.75h | Removed universities/junk; dedup to earliest -> ~8,200 firms |
| 2026-10-18 | 2 | Hand-review 25-row UUCP sample | 0.5h | Found ~15-25% false positives (schools, BBSes); added filters |
| 2026-10-18 | 3 | Aggregate sources + verify matching | 0.5h | Combined dataset; verified name-normalization |
| 2026-10-18 | 3 | Reshape to supervisors' target schema | 0.5h | Mapped to exact example columns + controlled vocab |
| 2026-10-18 | 4 | Analysis: summaries + figures | 0.5h | Found + documented UUCP coverage anomaly (1989-90 gap) |
| 2026-10-18 | 5 | Documentation (README, decisions, progress note) | 1h | — |
| 2026-10-18 | 5 | Push to GitHub | 0.5h | Remote URL + auth token setup |
| 2026-10-22 | 6 | Data-quality fixes (states, names, junk filter) | 0.5h | Recovered ~2,100 missing states |
| 2026-10-22 | 6 | Install + learn LinkTransformer | 0.25h | Slow first import; ML dependencies |
| 2026-10-22 | 6 | Dedup by state + address validation | 0.5h | — |
| 2026-10-22 | 6 | Debug clustering (SLINK chaining, threshold direction) | 1h | Caught over-merging (97% blob); switched to agglomerative, threshold 0.2 |
| 2026-10-22 | 6 | Found/fixed shared-facility confounder | 0.25h | 2 giant address groups polluted statistic |
| 2026-10-22 | 6 | Compute + write up dedup statistic | 0.5h | Final (corrected): 30.4% of address-dupes caught by name+state |
| 2026-10-26 | 7 | Source 3 (NSFNET): manual sample + first parser | 0.75h | Multi-line addresses, intl countries |
| 2026-10-26 | 7 | Bulk-download NANOG mbox archives (1992-94) | 0.5h | Found mbox export endpoint; 36 months |
| 2026-10-26 | 7 | Auto-extract 320 PRDB messages from mboxes | 0.5h | Subject matching + body extraction |
| 2026-10-26 | 7 | Fix dual-format parser (table + block layouts) | 1h | T1 section changed format mid-1992 |
| 2026-10-26 | 7 | Finalize + dedup NSFNET (9,407 -> firms, ~30 countries) | 0.5h | Earliest-appearance dedup |
| 2026-10-26 | 8 | Cross-source firm linking + per-network timelines | 0.5h | 285 multi-network firms |
| 2026-10-26 | 8 | Finding: UUCP->NSFNET gap analysis + chart | 0.5h | 95% email-first, median 1.1yr |
| 2026-10-26 | 8 | Documentation (findings.md, decisions, README) | 0.75h | — |
| 2026-10-26 | 8 | Repo cleanup (junk folders, tidy structure) | 0.25h | Removed stray folders from paste mishaps |
| 2026-10-26 | 9 | Diagnose LinkTransformer value vs. normalization | 0.5h | Found normalization already catches most variants |
| 2026-10-26 | 9 | Threshold tuning + cluster inspection (0.2 vs 0.1) | 0.75h | 0.2 over-merged same-template universities; chose 0.1 |
| 2026-10-26 | 9 | Fix academic filter (intl universities, protect "Universal") | 0.5h | 204 -> 0 academic rows; Universal firms kept |
| 2026-10-26 | 9 | Integrate LinkTransformer 0.1 into cross-source linking | 0.5h | 314 multi-network firms; finding robust to method |
| 2026-10-26 | 9 | Resolve git divergence (website vs local edits) | 0.25h | Merged README web-edit with local commits |
| 2026-10-26 | 9 | Documentation + professor update | 0.5h | dedup_analysis, findings, message |

Approximate total: ~23 hours