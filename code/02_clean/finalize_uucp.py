"""
Filter UUCP candidates to likely FIRMS and deduplicate to earliest appearance.
Maps to the project schema. Output reviewed by hand afterward.
"""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/interim/uucp_candidates.csv")
OUT = Path("data/clean/uucp_clean.csv")
FLAGGED = Path("data/interim/uucp_flagged_nonfirm.csv")

# Patterns that mark an org as academic / non-firm -> exclude from firm set
ACADEMIC_RE = re.compile(
    r"\b(univ|university|college|dept\.?|department|institute of tech|"
    r"school of|faculty|laborator|national lab|polytechnic|academ|"
    r"high school|elementary|middle school)",
    re.IGNORECASE)

# Patterns hinting at non-company nodes (BBS, personal, government)
AMBIGUOUS_RE = re.compile(
    r"\b(bbs|bulletin board|personal|home system|hobby|gov\b|\.gov|"
    r"city of|county of|public library)",
    re.IGNORECASE)

# Corporate signals -> boosts confidence it's a firm
FIRM_RE = re.compile(
    r"\b(inc\.?|corp\.?|corporation|co\.?|company|ltd\.?|llc|"
    r"systems|technolog|software|communications|labs?\b|"
    r"industries|associates|group|services)",
    re.IGNORECASE)


def clean_name(org):
    return re.sub(r"\s+", " ", str(org)).strip()


df = pd.read_csv(IN)
df["org"] = df["org"].fillna("").map(clean_name)

# Drop rows with no org text
df = df[df["org"] != ""].copy()

JUNK_RE = re.compile(
    r"^(not organized|private use|personal|none|n/?a|unknown|test)\b",
    re.IGNORECASE)
df = df[~df["org"].str.contains(JUNK_RE)].copy()

# Classify
df["is_academic"] = df["org"].str.contains(ACADEMIC_RE)
df["is_ambiguous"] = df["org"].str.contains(AMBIGUOUS_RE)
df["looks_like_firm"] = df["org"].str.contains(FIRM_RE)

# Separate the clearly-academic for a flagged file (so we don't silently lose them)
academic = df[df["is_academic"]].copy()
academic.to_csv(FLAGGED, index=False)

# Keep candidate firms: not academic
firms = df[~df["is_academic"]].copy()

# Deduplicate to EARLIEST appearance per organization
firms = firms.sort_values("connection_date")
firms = firms.drop_duplicates(subset=["org"], keep="first")

# Map to project schema
firms["firm_name_raw"] = firms["org"]
firms["firm_name_clean"] = firms["org"]
firms["network"] = "UUCP"
firms["network_category"] = "UUCP mail"
firms["date_precision"] = "month"
firms["event_type"] = "map appearance"
firms["location_raw"] = firms["postal"].fillna("")

# Try to pull ", City, ST ZIP" or ", City ST ZIP" from the postal field
def parse_city_state(postal):
    s = str(postal)
    m = re.search(r",\s*([A-Za-z .]+?),?\s+([A-Z]{2})\s+\d{5}", s)
    if m:
        return m.group(1).strip(), m.group(2)
    m = re.search(r",\s*([A-Za-z .]+?),?\s+([A-Z]{2})\b", s)
    if m:
        return m.group(1).strip(), m.group(2)
    return "", ""

cs = firms["postal"].fillna("").map(parse_city_state)
firms["city"] = [c for c, _ in cs]
firms["state"] = [s for _, s in cs]

firms["country"] = "USA"
firms["source"] = "uucp_map"
firms["source_url"] = "https://github.com/encse/uucp-map"
firms["source_quote"] = "#O " + firms["org"]
firms["confidence"] = firms["looks_like_firm"].map(
    {True: "medium", False: "low"})
base_note = "date = first appearance in available UUCP maps (coverage uneven; see decisions_log)"
amb = firms["is_ambiguous"].map(
    {True: " | flagged: possible BBS/personal/government node", False: ""})
firms["notes"] = base_note + amb

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
firms = firms.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
firms.to_csv(OUT, index=False)

print(f"Total candidate records in: {len(df)}")
print(f"Excluded as academic (saved to {FLAGGED.name}): {len(academic)}")
print(f"Unique candidate FIRMS (earliest appearance): {len(firms)}")
print()
print(firms[["firm_name_clean","connection_date","confidence"]].head(25).to_string())