# Deduplication Analysis — UUCP firms

## Method
- **Name+state matching (Method A):** LinkTransformer (all-MiniLM-L6-v2,
  SLINK clustering, cosine threshold 0.5) run *within each state*. Firms with
  similar names in the same state are grouped (firm_group_id).
- **Address matching (Method B):** records sharing a normalized address are
  treated as duplicates.

## Key statistic (requested)
Of record-pairs that share an address, what share are already caught by
name+state matching?

| Scope | Address-dup pairs | Also caught by name+state | Share |
|-------|-------------------|---------------------------|-------|
| California (test) | 206 | 177 | 85.9% |
| All states | 820 | 621 | **75.7%** |

**Interpretation:** name+state matching catches ~76% of address-based duplicates
on its own; address-matching uniquely identifies the remaining ~24%. Address
validation therefore adds meaningful but not dominant value.

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