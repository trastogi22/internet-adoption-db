"""
Parse NSFNET PRDB 'Additions' messages -> candidate org rows.
Handles BOTH layouts:
  A) Table format:  Net#  NetName  Primary Secondary  Location (wrapped)
  B) Block format:  Network IP: / Network Name: / Location: / Country Code:
Date from filename (YYYY_MM). Country parsed from address / Country Code field.
"""
import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/nsfnet_prdb")
OUT_FILE = Path("data/interim/nsfnet_candidates.csv")

DATE_IN_NAME = re.compile(r"(\d{4})[_-](\d{2})")

COUNTRIES = {
    "USA":"USA","US":"USA","CANADA":"CAN","SWITZERLAND":"CHE","ITALY":"ITA",
    "GERMANY":"DEU","FRANCE":"FRA","UK":"GBR","ENGLAND":"GBR","JAPAN":"JPN",
    "NETHERLANDS":"NLD","SWEDEN":"SWE","AUSTRALIA":"AUS","BELGIUM":"BEL",
    "SPAIN":"ESP","DENMARK":"DNK","NORWAY":"NOR","FINLAND":"FIN","MEXICO":"MEX",
    "ISRAEL":"ISR","KOREA":"KOR","TAIWAN":"TWN","AUSTRIA":"AUT","IRELAND":"IRL",
}
COUNTRY_RE = re.compile(r"\b(" + "|".join(COUNTRIES) + r")\b\.?\s*$", re.I)
CC_MAP = {"US":"USA","CA":"CAN","CH":"CHE","IT":"ITA","DE":"DEU","FR":"FRA",
          "GB":"GBR","UK":"GBR","JP":"JPN","NL":"NLD","SE":"SWE","AU":"AUS",
          "BE":"BEL","ES":"ESP","DK":"DNK","NO":"NOR","FI":"FIN","MX":"MEX",
          "IL":"ISR","KR":"KOR","TW":"TWN","AT":"AUT","IE":"IRL"}

TABLE_ROW = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){1,3})\s+(\S+)\s+\S+\s+\S+\s+(.*)$")


def file_date(path):
    m = DATE_IN_NAME.search(path.name)
    return f"{m.group(1)}-{m.group(2)}" if m else ""


def finish_loc(loc_lines, cc=""):
    loc = re.sub(r"\s+", " ", " ".join(loc_lines)).strip().rstrip(",")
    country = CC_MAP.get(cc.upper(), "") if cc else ""
    if not country:
        cm = COUNTRY_RE.search(loc)
        if cm:
            country = COUNTRIES.get(cm.group(1).upper(), "USA")
            loc = COUNTRY_RE.sub("", loc).strip().rstrip(",")
        else:
            country = "USA"
    org = loc.split(",")[0].strip()
    return org, loc, country


def parse_block_format(lines, date, fname, rows):
    """Format B: 'Network IP:' / 'Network Name:' / 'Location:' / 'Country Code:'"""
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        mip = re.match(r"\s*Network IP:\s*(\S+)", line)
        if mip:
            net = mip.group(1)
            netname, loc_lines, cc = "", [], ""
            j = i + 1
            while j < n:
                l = lines[j]
                if re.match(r"\s*Network IP:", l):
                    break
                mn = re.match(r"\s*Network Name:\s*(.*)", l)
                ml = re.match(r"\s*Location:\s*(.*)", l)
                mc = re.match(r"\s*Country Code:\s*(\S+)", l)
                if mn:
                    netname = mn.group(1).strip()
                elif ml:
                    loc_lines = [ml.group(1).strip()]
                    # gather continuation lines until Country Code or blank/next
                    k = j + 1
                    while k < n and not re.match(
                            r"\s*(Country Code:|Network IP:|\d+:\d+)", lines[k]) \
                            and lines[k].strip():
                        loc_lines.append(lines[k].strip())
                        k += 1
                    j = k - 1
                elif mc:
                    cc = mc.group(1).strip()
                j += 1
            if loc_lines:
                org, loc, country = finish_loc(loc_lines, cc)
                rows.append({"net_number": net, "net_name": netname,
                             "org": org, "address": loc, "country": country,
                             "connection_date": date, "source_file": fname})
            i = j
        else:
            i += 1


def parse_table_format(lines, date, fname, rows):
    """Format A: Net# NetName Primary Secondary Location (wrapped)."""
    in_t1 = False
    current = None

    def flush(rec):
        if not rec:
            return
        org, loc, country = finish_loc(rec["loc_lines"])
        rows.append({"net_number": rec["net"], "net_name": rec["netname"],
                     "org": org, "address": loc, "country": country,
                     "connection_date": date, "source_file": fname})

    for line in lines:
        if re.search(r"T1 Network", line):
            in_t1 = True; continue
        if re.search(r"T3 Network", line) or re.search(r"Total NSFNET T1", line):
            flush(current); current = None; in_t1 = False; continue
        if not in_t1:
            continue
        m = TABLE_ROW.match(line)
        if m and not line.strip().startswith("Net #"):
            flush(current)
            current = {"net": m.group(1), "netname": m.group(2),
                       "loc_lines": [m.group(3).strip()]}
        elif current and line.strip() and not re.match(r"^-+", line.strip()):
            current["loc_lines"].append(line.strip())
        elif current and not line.strip():
            flush(current); current = None
    flush(current)


def parse_file(path):
    rows = []
    date = file_date(path)
    text = path.read_text(errors="ignore")
    lines = text.splitlines()
    # Detect format: block format has 'Network IP:' labels
    if "Network IP:" in text:
        parse_block_format(lines, date, path.name, rows)
    else:
        parse_table_format(lines, date, path.name, rows)
    return rows


def main():
    files = sorted(RAW_DIR.glob("*.txt"))
    print(f"Parsing {len(files)} PRDB files...")
    all_rows = []
    for f in files:
        all_rows.extend(parse_file(f))
    df = pd.DataFrame(all_rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df)} candidate records to {OUT_FILE}")
    if len(df):
        print("By country:", df["country"].value_counts().head(10).to_dict())
        print(df[["net_number","org","country","connection_date"]].head(15).to_string())


if __name__ == "__main__":
    main()