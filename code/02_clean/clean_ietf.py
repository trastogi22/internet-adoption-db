"""
Parse IETF Internet Monthly Reports -> candidate firm rows.
Output is reviewed by hand afterward.
"""

import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/ietf_monthly_reports")
OUT_FILE = Path("data/interim/ietf_candidates.csv")

MONTHS = ("January February March April May June July August "
          "September October November December").split()
MONTH_RE = "|".join(MONTHS)

HEADER_RE = re.compile(r"new on-?line members|new members|newly connected",
                       re.IGNORECASE)
DATE_IN_TEXT = re.compile(rf"({MONTH_RE})\s+(\d{{4}})", re.IGNORECASE)
PAREN_DATE = re.compile(r"\(([^)]*\d{4}[^)]*)\)")
NOISE_RE = re.compile(r"Cooper|Internet Monthly Report|\[Page \d+\]")


def is_section_header(line, next_line):
    stripped = line.strip()
    next_dashes = (set(next_line.strip()) <= set("-")
                   and len(next_line.strip()) >= 3)
    return (stripped and stripped.isupper() and next_dashes
            and "INTERNET MONTHLY" not in stripped)


def find_current_network(lines, idx):
    for j in range(idx, -1, -1):
        nxt = lines[j + 1] if j + 1 < len(lines) else ""
        if is_section_header(lines[j], nxt):
            return lines[j].strip()
    return ""


def parse_file(path):
    rows = []
    text = path.read_text(errors="ignore").replace("\x0c", "")
    lines = text.splitlines()

    i = 0
    while i < len(lines):
        if HEADER_RE.search(lines[i]):
            header = lines[i].strip()
            network = find_current_network(lines, i)
            m = DATE_IN_TEXT.search(header)
            default_date = f"{m.group(1)} {m.group(2)}" if m else ""

            j = i + 1
            while j < len(lines):
                nxt = lines[j + 1] if j + 1 < len(lines) else ""
                stripped = lines[j].strip()

                # stop ONLY at a clear new section
                is_list_marker = (
                    re.match(r"^[A-Z]\.\s", stripped)
                    and not re.match(r"^[A-Z]\.\s*[A-Z]\.", stripped)
                )
                if is_list_marker:
                    break
                if is_section_header(lines[j], nxt):
                    break

                # skip noise + blanks; do NOT stop on them
                if stripped == "" or NOISE_RE.search(stripped):
                    j += 1
                    continue

                # an org line = indented, comma-containing, has letters
                if "," in stripped and re.search(r"[A-Za-z]", stripped):
                    override = PAREN_DATE.search(stripped)
                    override_date = override.group(1) if override else ""
                    name_and_loc = PAREN_DATE.sub("", stripped).strip()
                    rows.append({
                        "firm_name_raw": name_and_loc,
                        "network": network,
                        "reported_date_text": override_date or default_date,
                        "override_date_text": override_date,
                        "source_quote": header,
                        "source_file": path.name,
                        "line_number": j + 1,
                    })
                j += 1
            i = j
        else:
            i += 1
    return rows


def main():
    all_rows = []
    for f in sorted(RAW_DIR.glob("*.txt")):
        print(f"Parsing {f.name} ...")
        all_rows.extend(parse_file(f))

    df = pd.DataFrame(all_rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df)} candidate rows to {OUT_FILE}")
    if len(df):
        print(df[["firm_name_raw", "network", "reported_date_text"]].to_string())


if __name__ == "__main__":
    main()