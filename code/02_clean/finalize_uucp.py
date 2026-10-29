"""
Filter UUCP candidates to likely FIRMS and deduplicate to earliest appearance.
Upgrades: robust state extraction, strip trailing location from names,
expanded junk filter. Maps to project schema.
"""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/interim/uucp_candidates.csv")
OUT = Path("data/clean/uucp_clean.csv")
FLAGGED = Path("data/interim/uucp_flagged_nonfirm.csv")

# ---------- State extraction ----------
STATE_NAMES = {
    "alabama":"Alabama","alaska":"Alaska","arizona":"Arizona","arkansas":"Arkansas",
    "california":"California","colorado":"Colorado","connecticut":"Connecticut",
    "delaware":"Delaware","florida":"Florida","georgia":"Georgia","hawaii":"Hawaii",
    "idaho":"Idaho","illinois":"Illinois","indiana":"Indiana","iowa":"Iowa",
    "kansas":"Kansas","kentucky":"Kentucky","louisiana":"Louisiana","maine":"Maine",
    "maryland":"Maryland","massachusetts":"Massachusetts","michigan":"Michigan",
    "minnesota":"Minnesota","mississippi":"Mississippi","missouri":"Missouri",
    "montana":"Montana","nebraska":"Nebraska","nevada":"Nevada",
    "new hampshire":"New Hampshire","new jersey":"New Jersey","new mexico":"New Mexico",
    "new york":"New York","north carolina":"North Carolina","north dakota":"North Dakota",
    "ohio":"Ohio","oklahoma":"Oklahoma","oregon":"Oregon","pennsylvania":"Pennsylvania",
    "rhode island":"Rhode Island","south carolina":"South Carolina",
    "south dakota":"South Dakota","tennessee":"Tennessee","texas":"Texas","utah":"Utah",
    "vermont":"Vermont","virginia":"Virginia","washington":"Washington",
    "west virginia":"West Virginia","wisconsin":"Wisconsin","wyoming":"Wyoming",
}
ABBR = {
    "al":"Alabama","ak":"Alaska","az":"Arizona","ar":"Arkansas","ca":"California",
    "co":"Colorado","ct":"Connecticut","de":"Delaware","fl":"Florida","ga":"Georgia",
    "hi":"Hawaii","id":"Idaho","il":"Illinois","in":"Indiana","ia":"Iowa","ks":"Kansas",
    "ky":"Kentucky","la":"Louisiana","me":"Maine","md":"Maryland","ma":"Massachusetts",
    "mi":"Michigan","mn":"Minnesota","ms":"Mississippi","mo":"Missouri","mt":"Montana",
    "ne":"Nebraska","nv":"Nevada","nh":"New Hampshire","nj":"New Jersey","nm":"New Mexico",
    "ny":"New York","nc":"North Carolina","nd":"North Dakota","oh":"Ohio","ok":"Oklahoma",
    "or":"Oregon","pa":"Pennsylvania","ri":"Rhode Island","sc":"South Carolina",
    "sd":"South Dakota","tn":"Tennessee","tx":"Texas","ut":"Utah","vt":"Vermont",
    "va":"Virginia","wa":"Washington","wv":"West Virginia","wi":"Wisconsin","wy":"Wyoming",
    "dc":"District of Columbia",
}

def extract_state(addr):
    s = str(addr).lower()
    for key, full in STATE_NAMES.items():
        if re.search(rf"\b{re.escape(key)}\b", s):
            return full
    for ab, full in ABBR.items():
        if re.search(rf"\b{ab}\b\.?", s):
            return full
    return ""

def extract_city(addr, state_full):
    """Grab the token just before the state as a rough city guess."""
    s = str(addr)
    # look for ", City, ST" or ", City State"
    m = re.search(r",\s*([A-Za-z .]+?),?\s+[A-Za-z]{2,}\.?\s*\d{5}", s)
    if m:
        return m.group(1).strip()
    m = re.search(r",\s*([A-Za-z .]+?),?\s+[A-Z]{2}\b", s)
    if m:
        return m.group(1).strip()
    return ""

# ---------- Name cleaning ----------
def strip_trailing_location(name):
    """Remove a trailing ', City, ST/State' that leaked into the org name."""
    s = str(name)
    # trailing ", City, ST" or ", City, Fullstate" (state is 2+ letters)
    s = re.sub(r",\s*[A-Za-z. ]+,\s*[A-Za-z]{2,}\.?\s*$", "", s)
    return s.strip().rstrip(",").strip()

# ---------- Filters ----------
ACADEMIC_RE = re.compile(
    r"\b(universit(y|ies|aet|a|e)|universid(ad|ade)|"
    r"college|colleges|community college|"
    r"fachhochschule|hochschule|polytechnic|conservatoire|"
    r"institute of technolog|school of|faculty of)\b",
    re.IGNORECASE)

JUNK_RE = re.compile(
    r"^(not an organization|not organized|private\b|privately owned|"
    r"home system|home computer|personal\b|none\b|n/?a\b|unknown\b|test\b|"
    r"\(none\))",
    re.IGNORECASE)

FIRM_RE = re.compile(
    r"\b(?:inc\.?|corp\.?|corporation|co\.?|company|ltd\.?|llc|"
    r"systems|technolog|software|communications|labs?\b|"
    r"industries|associates|group|services)",
    re.IGNORECASE)


def clean_ws(x):
    return re.sub(r"\s+", " ", str(x)).strip()


df = pd.read_csv(IN)
df["org"] = df["org"].fillna("").map(clean_ws)
df = df[df["org"] != ""].copy()

# Remove junk/personal nodes
df = df[~df["org"].str.contains(JUNK_RE)].copy()

# Separate academics (exclude from firm set but keep a record)
df["is_academic"] = df["org"].str.contains(ACADEMIC_RE)
df[df["is_academic"]].to_csv(FLAGGED, index=False)
firms = df[~df["is_academic"]].copy()

# Clean names: strip leaked trailing location
firms["org_clean"] = firms["org"].map(strip_trailing_location)

# Dedup to earliest appearance per cleaned org
firms = firms.sort_values("connection_date")
firms = firms.drop_duplicates(subset=["org_clean"], keep="first")

# Extract state + city from postal
firms["state"] = firms["postal"].map(extract_state)
firms["city"] = firms.apply(
    lambda r: extract_city(r["postal"], r["state"]), axis=1)

# Confidence
firms["looks_like_firm"] = firms["org_clean"].str.contains(FIRM_RE)

# Map to schema
firms["firm_name_raw"] = firms["org"]
firms["firm_name_clean"] = firms["org_clean"]
firms["network"] = "UUCP"
firms["network_category"] = "UUCP mail"
firms["date_precision"] = "month"
firms["event_type"] = "map appearance"
firms["location_raw"] = firms["postal"].fillna("")
firms["country"] = "USA"
firms["source"] = "uucp_map"
firms["source_url"] = "https://github.com/encse/uucp-map"
firms["source_quote"] = "#O " + firms["org"]
firms["confidence"] = firms["looks_like_firm"].map({True:"medium", False:"low"})
firms["notes"] = ("date = first appearance in available UUCP maps "
                  "(coverage uneven; see decisions_log)")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
firms = firms.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
firms.to_csv(OUT, index=False)
print(f"Unique candidate FIRMS after cleaning: {len(firms)}")
print(f"  with state extracted: {(firms['state']!='').sum()}")
print(f"  with city extracted:  {(firms['city']!='').sum()}")
print(firms[["firm_name_clean","city","state","connection_date"]].head(15).to_string())