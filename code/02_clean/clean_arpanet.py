"""
Parse ARPANET/DDN directories (1974-1984) -> organizations.
Handles 3 organisation formats:
  1974: Python list-string  ['Org' 'Addr'...]
  1975: plain text (first element; noisy OCR)
  1978+: pipe-separated  Org | Dept | Addr
These are PERSON directories; we extract orgs, dedup people->orgs,
and take earliest appearance across snapshots.
"""
import re
import ast
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/arpanet_1978")
OUT = Path("data/clean/arpanet_clean.csv")

# file -> (date, network_label, confidence)
FILES = {
    "arpanet_directory_1974-06.csv": ("1974-06", "ARPANET", "medium"),
    "arpanet_directory_1975-07.csv": ("1975-07", "ARPANET", "low"),  # noisy OCR
    "arpanet_directory_1978-12.csv": ("1978-12", "ARPANET", "medium"),
    "arpanet_directory_1979-10.csv": ("1979-10", "ARPANET", "medium"),
    "arpanet_directory_1980-11.csv": ("1980-11", "ARPANET", "medium"),
    "arpanet_directory_1982-03.csv": ("1982-03", "ARPANET", "medium"),
    "ddn_directory_1984-06.csv":     ("1984-06", "DDN", "medium"),
}

def clean_org_name(raw):
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return ""
    # 1974 list-string: ['Org' 'Addr' ...] -> first quoted item
    if s.startswith("["):
        m = re.search(r"'([^']+)'", s)
        if m:
            s = m.group(1)
    # 1978+ pipe format -> first segment
    if "|" in s:
        s = s.split("|")[0]
    # squeeze spaced-out OCR: "A i r Force" -> "Air Force"
    s = re.sub(r"\b([A-Za-z]) (?=[A-Za-z]\b)", r"\1", s)
    # strip leading junk
    s = s.lstrip('"\'').strip()
    s = re.sub(r"^[\-\*/]\s*", "", s)
    s = re.sub(r"^\d+\s+(?=[A-Z])", "", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(",").strip()
    return s


def is_junk_org(name):
    n = str(name).strip()
    if len(n) < 4:
        return True
    if not re.match(r"^[A-Za-z]", n):          # must start with a letter
        return True
    if re.match(r"^\(.*\)$", n):               # "(Smokey)" nicknames
        return True
    if re.search(r"\(\d{3}\)\s*\d{3}", n):     # phone numbers
        return True
    if re.match(r"(?i)^(p\.?o\.?\s*box|box)\b", n):  # PO boxes
        return True
    alpha = sum(c.isalpha() for c in n)        # mostly non-alpha = code/junk
    if alpha < len(n) * 0.5:
        return True
    return False

def looks_like_person(name):
    """Detect OCR leakage of a person name into org field (1975 issue)."""
    # e.g. "IAMS. James L." or "1CKERMAN-LEWIS. Grace E."
    return bool(re.match(r"^[0-9A-Z'\-]+\.\s+[A-Z][a-z]+", str(name)))

def get_location(row, cols):
    if "city_state" in cols and pd.notna(row.get("city_state")):
        return str(row["city_state"]).strip()
    return ""

rows = []
for fname, (date, net, conf) in FILES.items():
    p = RAW / fname
    if not p.exists():
        print(f"missing {fname}, skipping")
        continue
    df = pd.read_csv(p)
    cols = df.columns
    n_before = len(df)
    for _, r in df.iterrows():
        org = clean_org_name(r.get("organisation", ""))
        if not org or len(org) < 3:
            continue
        if is_junk_org(org):          # <-- ADD THIS
            continue
        if conf == "low" and looks_like_person(org):
            continue
        rows.append({
            "org": org,
            "location_raw": get_location(r, cols),
            "host": str(r.get("host", "")).strip(),
            "date": date,
            "network": net,
            "confidence": conf,
            "source_file": fname,
        })
    print(f"{fname}: {n_before} people rows parsed")

df = pd.DataFrame(rows)
print(f"\nTotal person-org rows: {len(df)}")

# Dedup: unique org per snapshot first, then earliest appearance across snapshots
df = df.sort_values("date")
# earliest date per org
earliest = df.groupby("org", as_index=False).first()
print(f"Unique organizations (earliest appearance): {len(earliest)}")

# Map to schema
earliest["firm_name_raw"] = earliest["org"]
earliest["firm_name_clean"] = earliest["org"]
earliest["network_category"] = earliest["network"] + " (directory listing)"
earliest["connection_date"] = earliest["date"]
earliest["date_precision"] = "month"
earliest["event_type"] = "directory_listing"
earliest["city"] = ""
earliest["state"] = ""
earliest["country"] = "USA"   # refine below
earliest["source"] = "arpanet_ddn"
earliest["source_url"] = "transcribed ARPANET/DDN directories (professor-provided)"
earliest["source_quote"] = earliest["org"] + " [" + earliest["host"] + "]"
earliest["notes"] = ("appears in ARPANET/DDN directory " + earliest["date"] +
                     "; earliest directory appearance, not verified first "
                     "connection; transcribed (some OCR artifacts)")

# crude non-US detection from location/org
def detect_country(row):
    txt = (str(row["org"]) + " " + str(row["location_raw"])).lower()
    for w, iso in {"belgium":"BEL","norway":"NOR","hungary":"HUN","canada":"CAN",
                   "england":"GBR","germany":"DEU","france":"FRA"}.items():
        if w in txt:
            return iso
    return "USA"
earliest["country"] = earliest.apply(detect_country, axis=1)
earliest["location_raw"] = earliest["location_raw"].fillna("")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
out = earliest.reindex(columns=cols)
OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT, index=False)
print(f"Wrote {OUT}")
print("By year:", out["connection_date"].str[:4].value_counts().sort_index().to_dict())
print("By country:", out["country"].value_counts().to_dict())
print("\nSample orgs:")
print(out[["firm_name_clean","connection_date","country"]].head(20).to_string())