# Key Findings

## 1. Email-before-IP adoption progression
Of 285 firms observed on BOTH UUCP (email) and NSFNET (IP routing):
- 95.1% appeared on UUCP before NSFNET
- Median gap: 1.1 years (mean 2.4 years)
- Examples: Adobe (UUCP 1987 -> NSFNET 1992), 3M (1987 -> 1992),
  AIM Technology (1987 -> 1993)

Interpretation: firms adopted email connectivity before IP/internet
connectivity. See output/figures/uucp_to_nsfnet_gap.png.

CAVEAT: the two sources have non-overlapping date windows (UUCP 1987-1992,
NSFNET 1992-1994), which structurally biases toward "UUCP first." The 95%
and 1.1-year gap should be read as a lower bound on true lead time.

## 2. Deduplication statistic
Of address-based duplicate pairs, ~30% are also caught by name+state matching
(LinkTransformer, threshold 0.2) -> address-checking adds ~70% unique catches.
See docs/dedup_analysis.md.

## 3. Dataset scope
- 14,276 observations; 10,501 unique firms
- 3 network types: regional IP (JvNCnet), UUCP mail, NSFNET routing
- ~30 countries (USA, Germany, France, UK, Australia, Japan, Taiwan, ...)