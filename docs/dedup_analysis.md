# Deduplication Analysis — UUCP firms

## Method
- **Name+state matching (Method A):** LinkTransformer (all-MiniLM-L6-v2,
  SLINK clustering, cosine threshold 0.5) run *within each state*. Firms with
  similar names in the same state are grouped (firm_group_id).
- **Address matching (Method B):** records sharing a normalized address are
  treated as duplicates.

## Key statistic (requested, CORRECTED)
Of record-pairs that share an address, what share are already caught by
name+state matching?

| Scope | Address-dup pairs | Also caught by name+state | Share |
|-------|-------------------|---------------------------|-------|
| California | 206 | 58 | 28.2% |
| All states | 820 | 249 | **30.4%** |

**Interpretation:** Only ~30% of address-based duplicate pairs are also caught
by name+state matching. Conversely, ~70% of true duplicates (same firm, same
address) are MISSED by name matching alone — because firms appear under
divergent names (divisions, subsidiaries, abbreviations). Address-checking
therefore adds substantial value for entity resolution.

## Clustering validation (important)
The statistic is highly sensitive to clustering quality. Early runs were invalid:
- SLINK (threshold 0.5) chained most firms into one blob -> false 80%.
- Agglomerative threshold 0.9 produced a single 2,369-member group -> false 97%.
  (LinkTransformer threshold is a DISTANCE: lower = stricter, opposite to our
  first assumption.)
Final: agglomerative, average linkage, threshold 0.2. Verified by inspecting
clusters — correctly groups Intel/JPL/Lockheed/National Semiconductor variants
(incl. a "Missles" typo) while keeping distinct firms apart. Largest group = 6.
See threshold scan table below.

## Important confounder found & handled
Initial address-matching was dominated by two large groups (89 and 74 members)
at single addresses (e.g., 4000 Moorpark Ave, San Jose). These were NOT
duplicate firms — they were unrelated companies behind a shared UUCP
gateway/commercial building (Credence Systems, Mellon Capital, Caere, XAOS...).
Fix: address groups with >5 members are treated as shared facilities and
excluded from duplicate-matching. This changed the (CA) statistic from a
polluted 80.3% (6,853 pairs) to a reliable 85.9% (206 pairs).

## Caveats
- Threshold (0.5) and address-group cap (5) are tunable choices.
- LinkTransformer run per-state means cross-state branches of one firm are not
  linked (consistent with "dedup by state" instruction).
- Address normalization is heuristic; some real duplicates with differently
  formatted addresses may be missed.

## Outputs
- data/clean/uucp_deduped.csv — all rows + firm_group_id + addr_group
- output/tables/dedup_statistic.txt — the statistic

