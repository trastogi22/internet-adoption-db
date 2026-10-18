# Internet Adoption Database

Dataset of the month/year each company first connected to the internet or an
early predecessor (ARPANET, USENET, BITNET, NSFNET, regional IP networks, etc.).

Repo: https://github.com/trastogi22/internet-adoption-db

## Goal
Clean dataset: firm name, network, first-connection date, location, source, notes.

## Structure
- `code/` — scripts (download → clean → aggregate → analysis)
- `data/raw/` — unaltered source data (do not edit; large files gitignored)
- `data/interim/` — intermediate cleaned outputs
- `data/clean/` — final aggregated datasets (the deliverable)
- `docs/` — data dictionary, decisions log, progress note, source notes
- `output/` — figures and summary tables

## Setup
- conda create -n internet-db python=3.11 -y
- conda activate internet-db
- pip install -r requirements.txt

## How to run (in order)
- python code/02_clean/clean_ietf.py       # parse IETF reports -> candidates
- python code/02_clean/finalize_ietf.py    # IETF -> clean schema
- python code/02_clean/clean_uucp.py       # parse UUCP maps -> candidates
- python code/02_clean/finalize_uucp.py    # filter firms, dedup -> clean schema
- python code/03_aggregate/aggregate.py    # combine sources, derive first-connection
- python code/04_analysis/analysis.py      # summary tables + figures

Note: UUCP raw data must be cloned first:
Good — your README is close, but it's missing several things now that you've done much more work. Here's the updated version with everything that should be added.

What's missing / needs updating
Checkboxes aren't marked (both sources are done)
No GitHub link
Setup commands are run together on one line (should be separate)
Progress log stops at Source 1 (UUCP, aggregation, analysis not mentioned)
No "How to run" section (the script order)
No key findings / caveats (your best work isn't visible)
Open questions list is thin (you have 4 now)
No mention of outputs/deliverables (where the actual dataset lives)
Dates need fixing (2026-10-16 → 2026-10-18 per our last conversation)
Updated README
Open README.md in VS Code, select all (Cmd+A), delete, and paste this:

markdown
Copy code
# Internet Adoption Database

Dataset of the month/year each company first connected to the internet or an
early predecessor (ARPANET, USENET, BITNET, NSFNET, regional IP networks, etc.).

Repo: https://github.com/trastogi22/internet-adoption-db

## Goal
Clean dataset: firm name, network, first-connection date, location, source, notes.

## Structure
- `code/` — scripts (download → clean → aggregate → analysis)
- `data/raw/` — unaltered source data (do not edit; large files gitignored)
- `data/interim/` — intermediate cleaned outputs
- `data/clean/` — final aggregated datasets (the deliverable)
- `docs/` — data dictionary, decisions log, progress note, source notes
- `output/` — figures and summary tables

## Setup
conda create -n internet-db python=3.11 -y
conda activate internet-db
pip install -r requirements.txt

shell
Copy code

## How to run (in order)
python code/02_clean/clean_ietf.py       # parse IETF reports -> candidates
python code/02_clean/finalize_ietf.py    # IETF -> clean schema
python code/02_clean/clean_uucp.py       # parse UUCP maps -> candidates
python code/02_clean/finalize_uucp.py    # filter firms, dedup -> clean schema
python code/03_aggregate/aggregate.py    # combine sources, derive first-connection
python code/04_analysis/analysis.py      # summary tables + figures

kotlin
Copy code
Note: UUCP raw data must be cloned first:
git clone https://github.com/encse/uucp-map.git data/raw/uucp_maps 

## Sources incorporated
- [x] IETF Internet Monthly Reports (Oct 1992; 9 orgs, JvNCnet; high confidence)
- [x] UUCP Mapping Project (encse/uucp-map; 1987–1992; ~8,200 firms; medium/low)

## Key outputs
- `data/clean/first_connection_by_firm.csv` — one row per firm, earliest connection
- `data/clean/combined_observations.csv` — all firm-network-date observations
- `output/tables/` — firms by network / year / confidence
- `output/figures/` — firms_by_year.png, firms_by_network.png

## Key findings
- ~8,200 unique firms across the two sources; no cross-source overlap
  (expected — different networks/eras; name-matching logic verified).
- UUCP surfaces recognizable early adopters: Sun Microsystems, Texas
  Instruments, Xerox, Motorola, Hewlett-Packard, Pratt & Whitney, ITT.

## Important caveats
- UUCP dates = "first appearance in available map snapshots," NOT verified
  first connection. Snapshot coverage is uneven (1989: 2 files, 1990: 3 files),
  so those years are effectively missing and inflate 1991–1992.
- Left-censoring: firms on UUCP before Apr 1987 collapse to 1987-04.
- Firm filter has ~15–25% false positives (divisions, schools, BBSes).
- Dedup is by normalized exact name; divisions/variants not yet consolidated.

## Open questions
1. Scope of "firm": include non-private entities (schools, non-profits) or not?
2. UUCP date interpretation: is "first observed in maps" acceptable given the
   coverage caveat, or restrict to well-covered years?
3. Entity granularity: keep divisions/projects separate or consolidate to parents?
4. Target definition: first connection to ANY predecessor, or first IP/internet?

## Progress log
- 2026-10-13: Project initialized.
- 2026-10-18: Source 1 (IETF) complete end-to-end: download → parse → clean →
  schema → reviewed (9 firms).
- 2026-10-18: Source 2 (UUCP) complete: parse → filter → dedup (~8,200 firms);
  surfaced and documented snapshot-coverage caveat.
- 2026-10-18: Aggregation + analysis done; combined dataset, figures, tables.
- 2026-10-18: Pushed to GitHub.

