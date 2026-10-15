# Internet Adoption Database

Dataset of the month/year each company first connected to the internet
or an early predecessor (ARPANET, USENET, BITNET, NSFNET, regional IP networks, etc.).

## Goal
Clean dataset: firm name, network, first-connection date, location, source, notes.

## Structure
- `code/`       — scripts (download → clean → aggregate → analysis)
- `data/raw/`   — unaltered source data (do not edit)
- `data/interim/` — intermediate cleaned outputs
- `data/clean/` — final aggregated dataset
- `docs/`       — data dictionary, decisions log, source notes
- `output/`     — figures and tables

## Setup
conda create -n internet-db python=3.11 -y
conda activate internet-db
pip install -r requirements.txt

## Sources incorporated
- [ ] IETF Internet Monthly Reports
- [ ] UUCP Mapping Project (encse/uucp-map)

## Progress log
- 2025-10-16: Project initialized.

## Open questions
- How to define "first connection" across heterogeneous network types?
