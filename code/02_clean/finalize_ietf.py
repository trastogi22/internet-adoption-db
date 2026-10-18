"""Standardize IETF candidates into the project schema."""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/interim/ietf_candidates.csv")
OUT = Path("data/clean/ietf_clean.csv")

MONTHS = {m: f"{i:02d}" for i, m in enumerate(
    ["January","February","March","April","May","June","July",
     "August","September","October","November","December"], start=1)}
# handle abbreviations like "Sept." "Sep." "Oct."
ABBR = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
        "Jul":"07","Aug":"08","Sep":"09","Sept":"09","Oct":"10","Nov":"11","Dec":"12"}

SOURCE_URL = ("https://mailarchive.ietf.org/arch/msg/ietf/"
              "vyMFGQvQaegIxTuNAe52fCByCo0/")

def to_yyyy_mm(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    # find year
    ym = re.search(r"(\d{4})", text)
    if not ym:
        return ""
    year = ym.group(1)
    # try full month name
    for name, num in MONTHS.items():
        if name.lower() in text.lower():
            return f"{year}-{num}"
    # try abbreviation (strip trailing period)
    for abbr, num in ABBR.items():
        if re.search(rf"\b{abbr}\b\.?", text, re.IGNORECASE):
            return f"{year}-{num}"
    return f"{year}"  # year only if month not found

def split_name_loc(raw):
    """'S. C. Johnson Wax, Racine, WI' -> (name, city, state)."""
    parts = [p.strip() for p in raw.split(",")]
    state, city, name = "", "", raw
    if len(parts) >= 3:
        # last part = state, second-to-last = city, rest = name
        state = parts[-1]
        city = parts[-2]
        name = ", ".join(parts[:-2])
    elif len(parts) == 2:
        city = parts[-1]
        name = parts[0]
    return name, city, state

df = pd.read_csv(IN)

names, cities, states = zip(*df["firm_name_raw"].map(split_name_loc))
df["firm_name_clean"] = names
df["city"] = cities
df["state"] = states
df["country"] = "USA"
df["connection_date"] = df["reported_date_text"].map(to_yyyy_mm)
df["date_precision"] = "month"
df["network_category"] = "regional IP"
df["event_type"] = df["override_date_text"].apply(
    lambda x: "operational (reported)" if str(x).strip() else "operational")
df["location_raw"] = df["city"] + ", " + df["state"]
df["source"] = "ietf_imr"
df["source_url"] = SOURCE_URL
df["confidence"] = "high"
df["notes"] = ""

# Hand-review notes (keyed by raw name). Documented, reproducible.
NOTES = {
    "Trenton Public Schools": "non-firm: public school district",
    "KMPG Peat Marwick": "likely typo for KPMG Peat Marwick (accounting firm)",
    "ICD/Hearst": "subsidiary/division of Hearst",
    "The Consortium": "ambiguous entity name; identity unverified",
    "Data-Tech Institute": "possibly training institute; firm status unverified",
}
df["notes"] = df["firm_name_clean"].map(NOTES).fillna("")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
df = df.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Wrote {len(df)} rows to {OUT}")
print(df[["firm_name_clean","city","state","connection_date","network"]].to_string())