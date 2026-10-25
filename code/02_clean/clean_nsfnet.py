"""
Parse NSFNET PRDB 'Additions to the routing database' messages.

Parses the T1 Network table: Net#, Net Name, Primary, Secondary, Location
(org + multi-line address ending in a country). Joins wrapped address lines.

Note: the T3 section largely repeats T1 nets (migrations); we parse T1 only
to avoid double-counting, and record that caveat.
"""
import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/nsfnet_prdb")
OUT_FILE = Path("data/interim/nsfnet_candidates.csv")

# Date from filename like prdb_1992_03.txt -> 1992-03
DATE_IN_NAME = re.compile(r"(\d{4})[-_](\d{2})")

# A record starts with a net number at the left margin:
#   "131.201         HI-RESG-NET        267       266       Honeywell..."
# Net number = digits and dots. Net name = next token. Then codes. Then location.
RECORD_START = re.compile(
    r"^(\d{1,3}(?:\.\d{1,3}){1,3})\s+(\S+)\s+(\S+)?\s*(\S+)?\s+(.*)$")

# Known country words to detect the end of an address
COUNTRIES = {
    "USA":"USA","US":"USA","CANADA":"CAN","SWITZERLAND":"CHE","ITALY":"ITA",
    "GERMANY":"DEU","FRANCE":"FRA","UK":"GBR","ENGLAND":"GBR",
    "NETHERLANDS":"NLD","JAPAN":"JPN","SWEDEN":"SWE","AUSTRALIA":"AUS",
    "BELGIUM":"BEL","SPAIN":"ESP","DENMARK":"DNK","NORWAY":"NOR","FINLAND":"FIN",
}
COUNTRY_RE = re.compile(r"\b(" + "|".join(COUNTRIES.keys()) + r")\b\.?\s*$",
                        re.IGNORECASE)


def file_date(path):
    m = DATE_IN_NAME.search(path.name)
    return f"{m.group(1)}-{m.group(2)}" if m else ""


def parse_file(path):
    rows = []
    date = file_date(path)
    lines = path.read_text(errors="ignore").splitlines()

    # Only parse the T1 Network section (stop at "T3 Network")
    in_t1 = False
    i = 0
    current = None

    def flush(rec):
        if not rec:
            return
        loc = re.sub(r"\s+", " ", " ".join(rec["loc_lines"])).strip().rstrip(",")
        # country
        country = "USA"
        cm = COUNTRY_RE.search(loc)
        if cm:
            country = COUNTRIES.get(cm.group(1).upper(), "USA")
            loc = COUNTRY_RE.sub("", loc).strip().rstrip(",")
        # org = text before the first comma (rough); keep full loc as address
        org = loc.split(",")[0].strip()
        rows.append({
            "net_number": rec["net"],
            "net_name": rec["netname"],
            "org": org,
            "address": loc,
            "country": country,
            "connection_date": date,
            "source_file": path.name,
        })

    while i < len(lines):
        line = lines[i]
        if re.search(r"^\s*T1 Network", line):
            in_t1 = True
            i += 1
            continue
        if re.search(r"^\s*T3 Network", line):
            flush(current); current = None
            break
        if re.search(r"Total NSFNET T1", line):
            flush(current); current = None
            in_t1 = False
            i += 1
            continue

        if in_t1:
            m = RECORD_START.match(line)
            # a record line starts with a net number AND isn't the header
            if m and not line.strip().startswith("Net #"):
                flush(current)
                current = {
                    "net": m.group(1),
                    "netname": m.group(2),
                    "loc_lines": [m.group(5).strip()],
                }
            elif current is not None and line.strip():
                # continuation of the address (indented wrap line)
                if not re.match(r"^-+", line.strip()):
                    current["loc_lines"].append(line.strip())
            elif current is not None and not line.strip():
                # blank line ends a record
                flush(current); current = None
        i += 1

    flush(current)
    return rows


def main():
    all_rows = []
    for f in sorted(RAW_DIR.glob("*.txt")):
        print(f"Parsing {f.name} ...")
        all_rows.extend(parse_file(f))
    df = pd.DataFrame(all_rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df)} candidate records to {OUT_FILE}")
    if len(df):
        print(df[["net_number","net_name","org","country"]].head(25).to_string())


if __name__ == "__main__":
    main()