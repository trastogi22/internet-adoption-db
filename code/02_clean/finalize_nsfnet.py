"""Filter + map NSFNET PRDB candidates to project schema."""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/interim/nsfnet_candidates.csv")
OUT = Path("data/clean/nsfnet_clean.csv")

ACADEMIC_RE = re.compile(
    r"\b(univ|university|college|institute of tech|studi|universita|"
    r"school of|polytechnic)\b", re.IGNORECASE)

def clean_ws(x):
    return re.sub(r"\s+", " ", str(x)).strip()

df = pd.read_csv(IN)
df["org"] = df["org"].fillna("").map(clean_ws)

# Flag academics (exclude from firm set)
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
firms["city"] = ""     # could parse later from address
firms["state"] = ""
firms["source"] = "nsfnet_prdb"
firms["source_url"] = ("https://lists.nanog.org/archives/list/"
                       "nanog@lists.nanog.org/1992/3/")
firms["source_quote"] = firms["net_number"] + " " + firms["net_name"] + " " + firms["org"]
firms["confidence"] = "medium"
firms["notes"] = ("routing-database addition, not verified first connection; "
                  "T3 migrations excluded to avoid double-counting")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
firms = firms.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
firms.to_csv(OUT, index=False)
print(f"Wrote {len(firms)} firms to {OUT}")
print(f"  excluded as academic: {df['is_academic'].sum()}")
print(f"  countries: {firms['country'].value_counts().to_dict()}")
print(firms[["firm_name_clean","country","connection_date"]].to_string())