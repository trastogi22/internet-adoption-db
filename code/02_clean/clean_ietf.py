import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/ietf_monthly_reports")
OUT_FILE = Path("data/interim/ietf_candidates.csv")

MONTHS = ("January February March April May June July August "
          "September October November December").split()
MONTH_RE = "|".join(MONTHS)

# starts a "new members" block
HEADER_RE = re.compile(r"new on-?line members|new members|newly connected",
                       re.IGNORECASE)

# locate "October 1992" anywhere in a line
DATE_IN_TEXT = re.compile(rf"({MONTH_RE})\s+(\d{{4}})", re.IGNORECASE)

# parenthetical override like "(Sept. 1992)" or "(September 1992)"
PAREN_DATE = re.compile(r"\(([^)]*\d{4}[^)]*)\)")


def find_current_network(lines, idx):
    """Walk backwards to find the most recent ALL-CAPS network header."""
    for j in range(idx, -1, -1):
        line = lines[j].strip()
        # Network headers are ALL CAPS, short-ish, not page footers
        if (line and line.isupper() and len(line) < 60
                and "INTERNET MONTHLY" not in line
                and "TABLE OF CONTENTS" not in line
                and "CALENDAR" not in line):
            return line
    return ""


def parse_file(path):
    rows = []
    lines = path.read_text(errors="ignore").splitlines()

    i = 0
    while i < len(lines):
        if HEADER_RE.search(lines[i]):
            header = lines[i].strip()
            network = find_current_network(lines, i)

            # default month from the header text
            m = DATE_IN_TEXT.search(header)
            default_date = f"{m.group(1)} {m.group(2)}" if m else ""

            # collect indented org lines that follow
            j = i + 1
            while j < len(lines):
                raw = lines[j]
                stripped = raw.strip()

                # stop conditions: blank line, a new lettered section (B.),
                # a page footer, or another header
                if stripped == "":
                    # allow a single blank? No—blank ends the block here.
                    break
                if re.match(r"^[A-Z]\.\s", stripped):   # "B.  ..."
                    break
                if "Cooper" in stripped or "Internet Monthly Report" in stripped:
                    j += 1
                    continue
                # must be indented (org lines are deeply indented)
                if len(raw) - len(raw.lstrip()) < 8:
                    break

                # extract override date if present
                override = PAREN_DATE.search(stripped)
                override_date = override.group(1) if override else ""
                name_and_loc = PAREN_DATE.sub("", stripped).strip()

                rows.append({
                    "firm_name_raw": name_and_loc,
                    "network": network.title(),
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