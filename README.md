# Internet Adoption Database

Dataset of the month/year each company first connected to the internet or an
early predecessor (ARPANET, USENET, BITNET, NSFNET, regional IP networks, etc.).

Repo: https://github.com/trastogi22/internet-adoption-db

## Goal
Clean dataset: firm name, network, first-connection date, location, source, notes.

## Structure
- code/ — scripts (download -> clean -> aggregate -> analysis)
- data/raw/ — unaltered source data (do not edit; large files gitignored)
- data/interim/ — intermediate cleaned outputs
- data/clean/ — final aggregated datasets (the deliverable)
- docs/ — data dictionary, decisions log, findings, progress notes
- output/ — figures and summary tables

## Setup
    conda create -n internet-db python=3.11 -y
    conda activate internet-db
    pip install -r requirements.txt

## How to run (in order)
First clone the UUCP raw data:

    git clone https://github.com/encse/uucp-map.git data/raw/uucp_maps

IETF + UUCP:

    python code/02_clean/clean_ietf.py
    python code/02_clean/finalize_ietf.py
    python code/02_clean/clean_uucp.py
    python code/02_clean/finalize_uucp.py

NSFNET PRDB (bulk download + extract from NANOG mbox archives):

    python code/01_download/download_nsfnet_mbox.py      # download monthly mboxes
    python code/01_download/extract_prdb_from_mbox.py    # extract PRDB messages
    python code/02_clean/clean_nsfnet.py                 # parse (dual-format)
    python code/02_clean/finalize_nsfnet.py              # filter, dedup -> schema

Aggregate + analyze:

    python code/03_aggregate/aggregate.py                # combine sources
    python code/03_aggregate/dedup.py                    # LinkTransformer dedup + statistic
    python code/03_aggregate/match_target_schema.py      # deliverable in target schema
    python code/04_analysis/analysis.py                  # summary tables + figures
    python code/04_analysis/cross_source.py              # cross-source firm timelines

## Sources incorporated
- [x] IETF Internet Monthly Reports (Oct 1992; 9 orgs, JvNCnet; high confidence)
- [x] UUCP Mapping Project (encse/uucp-map; 1987-1992; ~8,200 firms; medium/low)
- [x] NSFNET PRDB routing additions (1992-1994; 5,642 firms; ~30 countries; medium)

## Dataset at a glance
- 14,276 observations; 10,501 unique firms
- 3 network types: regional IP (JvNCnet), UUCP mail, NSFNET routing
- ~30 countries (USA, Germany, France, UK, Australia, Japan, Taiwan, ...)

## Key outputs
- data/clean/firm_internet_connectivity.csv — **MAIN DELIVERABLE** (matches the
  provided example schema): one row per observed connectivity event (~14,300 rows,
  all three sources), with firm_group_id for within-source firm linking.
- data/clean/firm_network_timeline.csv — first connection per firm per network
- output/tables/multi_network_firms.csv — firms appearing in >1 network
- output/figures/ — firms_by_year, firms_by_network, uucp_to_nsfnet_gap

## Key findings
- **Email before IP:** of 285 firms observed on both UUCP (email) and NSFNET
  (IP routing), 95% appeared on UUCP first, median 1.1 years earlier (e.g.,
  Adobe: UUCP 1987 -> NSFNET 1992). Suggests firms adopted email before IP
  connectivity. (Caveat below.)
- **Dedup statistic:** only ~30% of address-based duplicate pairs are also caught
  by name+state matching (LinkTransformer, threshold 0.2), so address-checking
  uniquely identifies ~70% of duplicates. See docs/dedup_analysis.md.
- Recognizable early adopters surfaced: Sun Microsystems, Texas Instruments,
  Xerox, Motorola, Hewlett-Packard, Adobe, 3M, MCI, plus international firms.

## Important caveats
- **Source date windows differ** (UUCP 1987-92, NSFNET 1992-94), which biases the
  "email before IP" finding toward UUCP-first; read the 1.1-year gap as a lower bound.
- UUCP dates = "first appearance in available map snapshots," NOT verified first
  connection. Coverage is uneven (1989: 2 files, 1990: 3 files), inflating 1991-92.
- NSFNET dates = routing-database addition announcements, not verified live
  connectivity; weekly messages deduped to earliest appearance; includes some
  T1->T3 migrations of already-connected nets.
- Left-censoring: firms on UUCP before Apr 1987 collapse to 1987-04.
- Firm filter has ~15-25% false positives (divisions, schools, BBSes).
- Dedup validated by inspecting clusters; earlier attempts over-merged (SLINK
  chaining) before switching to agglomerative/threshold 0.2.

## Open questions / supervisor guidance
1. Scope of "firm": exclude universities/schools; keep non-profits separately
   (per supervisor guidance). Non-school non-profits of separate interest.
2. UUCP date interpretation: "first observed in maps" accepted (per supervisor).
3. Entity granularity: keep branches granular, link to parent for roll-up
   (per supervisor); firm_group_id implemented within-source; cross-source
   linking is next.
4. Target: any predecessor, tracking each first connection per network
   (per supervisor) — implemented via per-network timelines.

## Progress log
- 2026-10-13: Project initialized.
- 2026-10-18: Sources 1-2 (IETF, UUCP) complete; aggregation, analysis, docs;
  pushed to GitHub.
- 2026-10-22: LinkTransformer dedup + address validation; corrected clustering
  (SLINK blob -> agglomerative 0.2); statistic 30.4%; shared-facility fix.
- 2026-10-25: Source 3 (NSFNET) expanded to full 1992-94 via bulk mbox download
  + 320-message extraction; dual-format parser; ~30 countries.
- 2026-10-25: Cross-source linking; finding: 95% email-before-IP, median 1.1yr.
