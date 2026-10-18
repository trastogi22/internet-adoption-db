"""
Parse UUCP map files -> candidate organization rows.

Format: records of #X<TAB>value lines, separated by '#'.
  #N node name, #O organization, #P postal address.
Date comes from the FILENAME (ISO timestamp), NOT the #W edit field.

Scope: processes USA state maps (files named u.usa.*) by default.
Output is reviewed by hand afterward.
"""

import re
from pathlib import Path
import pandas as pd

MAPS_DIR = Path("data/raw/uucp_maps/files")
OUT_FILE = Path("data/interim/uucp_candidates.csv")

# Which files to parse. Start with USA state node-maps only.
FILE_GLOB = "**/u.usa.*"

# Pull the ISO date (YYYY-MM-DD) out of the filename.
DATE_IN_NAME = re.compile(r"(\d{4})-(\d{2})-(\d{2})T")

# A field line like "#O<tab or spaces>value"
FIELD_RE = re.compile(r"^#([A-Z])\s+(.*)$")

# Lines belonging to the shell-archive wrapper, to ignore
WRAPPER_RE = re.compile(r"^(:|echo shar|cat <<|SHAR_EOF|#Filename|#Packaged)")


def file_date(path):
    m = DATE_IN_NAME.search(path.name)
    if m:
        return f"{m.group(1)}-{m.group(2)}"   # YYYY-MM
    return ""


def parse_file(path):
    rows = []
    date = file_date(path)
    lines = path.read_text(errors="ignore").splitlines()

    record = {}
    def flush():
        # save a record if it has a node name
        if record.get("N"):
            rows.append({
                "node": record.get("N", "").strip(),
                "org": record.get("O", "").strip(),
                "postal": record.get("P", "").strip(),
                "contact": record.get("C", "").strip(),
                "connection_date": date,
                "source_file": path.name,
            })

    for line in lines:
        if WRAPPER_RE.search(line):
            continue
        # record separator: a line that is just "#"
        if line.strip() == "#":
            flush()
            record = {}
            continue
        m = FIELD_RE.match(line)
        if m:
            letter, value = m.group(1), m.group(2)
            # keep only the first occurrence of each field per record
            if letter not in record:
                record[letter] = value
    flush()  # last record
    return rows


def main():
    files = sorted(MAPS_DIR.glob(FILE_GLOB))
    print(f"Found {len(files)} matching map files.")
    all_rows = []
    for f in files:
        all_rows.extend(parse_file(f))

    df = pd.DataFrame(all_rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df)} candidate records to {OUT_FILE}")
    if len(df):
        print(df[["node", "org", "connection_date"]].head(20).to_string())


if __name__ == "__main__":
    main()