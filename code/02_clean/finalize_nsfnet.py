"""Filter + dedup NSFNET PRDB candidates to earliest appearance, map to schema."""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/interim/nsfnet_candidates.csv")
OUT = Path("data/clean/nsfnet_clean.csv")

ACADEMIC_RE = re.compile(
    r"\b(univ|university|college|institute of tech|studi|universit[ae]|"
    r"school of|polytechnic|hochschule|ecole|academ)\b", re.IGNORECASE)

ISO3 = {"USA":"USA","CAN":"CAN","CHE":"CHE","ITA":"ITA","DEU":"DEU","FRA":"FRA",
        "GBR":"GBR","JPN":"JPN","NLD":"NLD","SWE":"SWE","AUS":"AUS","BEL":"BEL",
        "ESP":"ESP","DNK":"DNK","NOR":"NOR","FIN":"FIN","MEX":"MEX","ISR":"ISR",
        "KOR":"KOR","TWN":"TWN","AUT":"AUT","IRL":"IRL"}

def clean_ws(x):
    return re.sub(r"\s+", " ", str(x)).strip()

df = pd.read_csv(IN)
df["org"] = df["org"].fillna("").map(clean_ws)
df = df[df["org"] != ""].copy()

# Dedup to EARLIEST appearance per network+org (collapses weekly repeats)
df = df.sort_values("connection_date")
df = df.drop_duplicates(subset=["net_number", "org"], keep="first")

# Flag + exclude academics
df["is_academic"] = df["org"].str.contains(ACADEMIC_RE)
firms = df[~df["is_academic"]].copy()

# Map to schema
firms["firm_name_raw"] = firms["org"]
firms["firm_name_clean"] = firms["org"]
firms["network"] = "NSFNET"
firms["network_category"] = "NSFNET (routing record)"
firms["date_precision"] = "month"
firms["event_type"] = "routing_addition_announced"
firms["location_raw"] = firms["address"].fillna("")
firms["city"] = ""
firms["state"] = ""
firms["country"] = firms["country"].map(lambda c: ISO3.get(str(c), str(c)))
firms["source"] = "nsfnet_prdb"
firms["source_url"] = "https://lists.nanog.org/archives/list/nanog@lists.nanog.org/"
firms["source_quote"] = firms["net_number"] + " " + firms["net_name"].fillna("") + " " + firms["org"]
firms["confidence"] = "medium"
firms["notes"] = ("routing-database addition, not verified first connection; "
                  "earliest appearance across weekly PRDB messages")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
firms = firms.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
firms.to_csv(OUT, index=False)
print(f"Candidates in: {len(df)} (after earliest-appearance dedup)")
print(f"Excluded as academic: {df['is_academic'].sum()}")
print(f"NSFNET firms out: {len(firms)}")
print("By country:", firms['country'].value_counts().head(12).to_dict())
print("By year:", firms['connection_date'].str[:4].value_counts().sort_index().to_dict())