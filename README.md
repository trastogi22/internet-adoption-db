# Internet Adoption Database

Dataset of the month/year each company first connected to the internet or an
early predecessor (ARPANET, UUCP/USENET, NSFNET, regional IP networks).

Repo: https://github.com/trastogi22/internet-adoption-db

## Goal
Clean dataset: firm name, network, first-connection date, location, entity type,
source, notes.

## Dataset at a glance
- **19,545 observations** across **4 sources**, spanning **1974–1994**
- **15,646 firm-classified observations** -> **~11,582 unique firms** after
  cross-source dedup (LinkTransformer)
- (+ schools/military/government/infrastructure, flagged + filterable)
- 22 countries (USA-dominated; international firms mainly via NSFNET)

## Structure
- code/ — scripts (download -> clean -> aggregate -> analysis)
- data/raw/ — unaltered source data (do not edit; large files gitignored)
- data/interim/ — intermediate cleaned outputs
- data/clean/ — final aggregated datasets (the deliverable)
- docs/ — data dictionary, decisions log, findings, sources roadmap
- output/ — figures (maps, adoption charts) and tables (funnel, multi-network)

## Setup
    conda create -n internet-db python=3.11 -y
    conda activate internet-db
    pip install -r requirements.txt

## How to run (in order)
Clone UUCP raw data first:

    git clone https://github.com/encse/uucp-map.git data/raw/uucp_maps

ARPANET/DDN (transcribed directories in data/raw/arpanet_1978/):

    python code/02_clean/clean_arpanet.py

IETF Monthly Reports (bulk download 108 reports + parse new-member sections):

    python code/01_download/download_imr.py
    python code/02_clean/clean_ietf_bulk.py
    python code/02_clean/finalize_ietf_bulk.py

UUCP:

    python code/02_clean/clean_uucp.py
    python code/02_clean/finalize_uucp.py

NSFNET PRDB (bulk download + extract from NANOG mbox archives):

    python code/01_download/download_nsfnet_mbox.py
    python code/01_download/extract_prdb_from_mbox.py
    python code/02_clean/clean_nsfnet.py
    python code/02_clean/finalize_nsfnet.py

Aggregate + classify + analyze:

    python code/03_aggregate/aggregate.py              # combine sources
    python code/03_aggregate/match_target_schema.py    # deliverable schema
    python code/03_aggregate/classify_entity.py        # entity_type field
    python code/04_analysis/funnel.py                  # sample funnel (raw->clean)
    python code/04_analysis/cross_source.py            # cross-source timelines + finding
    python code/04_analysis/adoption_viz.py            # adoption-over-time charts
    python code/04_analysis/country_map.py             # country choropleth maps

## Sources incorporated
- [x] ARPANET/DDN directories (1974–1984; 7 snapshots; ~2,800 orgs; transcribed)
- [x] UUCP Mapping Project (encse/uucp-map; 1987–1992; ~9,400 firms; medium/low)
- [x] NSFNET PRDB routing additions (1992–1993; ~7,000 rows; medium)
- [x] IETF Internet Monthly Reports (108 reports 1988–96; 277 member-firms 1991–94; high confidence)

## entity_type field
Each row classified: firm / school / military / government / infrastructure.
Lets analyses include/exclude groups. Firms (15,646 observations; ~11,582 unique
after cross-source dedup) are the main analysis set; the other ~3,900 observations
are retained but filterable.

## Key outputs
- data/clean/firm_internet_connectivity.csv — **MAIN DELIVERABLE** (one row per
  observed connectivity event; includes entity_type and firm_group_id
  [within-source; cross-source unique-firm linking via global_firm_id in
  cross_source.py])
- data/clean/firm_network_timeline.csv — first connection per firm per network
- output/tables/ — sample funnel, multi-network firms
- output/figures/ — country_map(_log), adoption_by_network, adoption_cumulative,
  adoption_by_country (US vs intl), uucp_to_nsfnet_gap

## Key findings
- **Timeline 1974–1994**, full arc ARPANET -> UUCP -> NSFNET + regional IP.
- **IETF expansion:** bulk-parsed 108 Monthly Reports -> IETF source grew from
  9 to 277 high-confidence member-firms; ~205 genuinely new to the dataset
  (regional-network members: JvNCnet/NEARnet/PREPnet), ~31 corroborate existing
  firms (via LinkTransformer). Note: IETF is high-confidence but modest volume
  (~2% of observations) — adds regional coverage/quality more than aggregate scale.
- **Email before IP:** of 305 firms observed on both UUCP (email) and NSFNET (IP
  routing), ~95% appeared on UUCP first, median ~1.1 years earlier (robust to
  exact vs. LinkTransformer matching). e.g., Adobe: UUCP 1987 -> NSFNET 1992.
- **Sample funnel:** large raw->clean reductions are deduplication of repeat
  observations (e.g., UUCP 113k records -> 9.4k firms = same firms across monthly
  maps), NOT discarded data. Reproducible via code/04_analysis/funnel.py.
- **Dedup method:** normalized-name matching + LinkTransformer (agglomerative,
  threshold 0.1 cross-source / 0.2 within-source, blocked by state/country),
  validated by cluster inspection. 11,582 unique firms; 439 span >1 network.
  See docs/dedup_analysis.md.
- Recognizable early adopters: Xerox PARC, BBN, Sun, TI, Motorola, HP, Adobe,
  3M, plus international firms.

## Important caveats
- Dates = "first observed in source," NOT verified first connection.
- Coverage gaps: 1985–86 (no source), UUCP 1989–90 (sparse snapshots) —
  annotated on all charts; not real adoption pauses.
- Source date windows differ (ARPANET 1974–84, UUCP 1987–92, NSFNET 1992–93,
  IETF 1991–94), biasing the email-before-IP gap; read as a lower bound.
- ARPANET/DDN: transcribed from scans (some OCR artifacts); entity_type noisier
  (cryptic 1970s–80s military codes); early-era "firm" subset should be spot-checked.
- UUCP dates = first appearance in available map snapshots; left-censored at 1987-04.
- NSFNET = routing-database announcements; weekly messages deduped to earliest;
  includes some T1->T3 migrations of already-connected nets.
- USA dominance partly real, partly source coverage (UUCP/ARPANET US-heavy).
- firm_group_id in the main CSV is within-source only; cross-source unique-firm
  linking lives in cross_source.py (global_firm_id). TODO: write global_firm_id
  back into the main deliverable for a unified ID.
- BITNET evaluated and excluded (unverifiable single-snapshot source).

## Open questions / supervisor guidance
- Scope of "firm": universities/schools excluded from the firm set but retained +
  flagged via entity_type; military kept + flagged (per supervisor).
- UUCP/ARPANET date interpretation: "first observed" accepted (per supervisor).
- Entity granularity: branches kept granular; cross-source unique-firm linking via
  LinkTransformer (global_firm_id in cross_source.py).
- Target: any predecessor, tracking first connection per network (per supervisor)
  — implemented via per-network timelines.
- Next: breadth (Harte Hanks/Aberdeen representative panel, needs access) vs.
  depth (more early-adopter sources: CSNET, HOSTS.TXT, RFCs). Early-adopter
  sources add quality but modest volume; Harte Hanks is the lever for scale.
  See professor correspondence.

## Progress log
- 2026-10-13: Project initialized.
- 2026-10-18: Sources IETF + UUCP; aggregation, analysis, docs; pushed.
- 2026-10-22: LinkTransformer dedup (validated); clustering corrected
  (SLINK blob -> agglomerative 0.2); dedup statistic; shared-facility fix.
- 2026-10-25: NSFNET expanded to full 1992–93 via bulk mbox download +
  320-message extraction; dual-format parser.
- 2026-11-05: entity_type classification (firm/school/military/gov/infra);
  cross-source finding (95% email-before-IP); refined academic/military filters.
- 2026-11-07: ARPANET/DDN integrated (1974–84) -> timeline now 1974–1994;
  sample funnel, country maps, two-panel adoption charts.
- 2026-11-17: Bulk-downloaded + parsed 108 IETF Monthly Reports -> IETF source
  9 -> 277 firms (~205 new, ~31 overlap); dataset now 19,545 obs, 1974–1994,
  ~11,582 unique firms.