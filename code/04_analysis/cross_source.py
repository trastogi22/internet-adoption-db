"""
Cross-source firm linking + per-network first-connection timeline.
Normalizes firm names, groups across all sources, and reports firms that
appear in multiple network types (the UUCP->NSFNET progression).
"""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/clean/firm_internet_connectivity.csv")
OUT_TIMELINE = Path("data/clean/firm_network_timeline.csv")
OUT_MULTI = Path("output/tables/multi_network_firms.csv")
TAB = Path("output/tables")
TAB.mkdir(parents=True, exist_ok=True)

SUFFIX = (r"\b(inc|incorporated|corp|corporation|co|company|ltd|llc|lp|plc|"
          r"gmbh|ag|sa|srl|bv|nv)\b\.?")

def norm(s):
    s = str(s).lower()
    s = re.sub(r"[.,;/()]", " ", s)
    s = re.sub(SUFFIX, " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

df = pd.read_csv(IN)
df["name_key"] = df["firm_name_standardized"].map(norm)
df = df[df["name_key"] != ""]

# earliest connection per firm PER network type
timeline = (df.sort_values("recorded_date")
              .groupby(["name_key", "connectivity_type"], as_index=False)
              .first()[["name_key","firm_name_standardized","connectivity_type",
                        "recorded_date","location_country_iso3"]])
timeline.to_csv(OUT_TIMELINE, index=False)

# firms in >1 network type
net_counts = df.groupby("name_key")["connectivity_type"].nunique()
multi_keys = net_counts[net_counts > 1].index
multi = timeline[timeline["name_key"].isin(multi_keys)].sort_values(
    ["name_key","recorded_date"])
multi.to_csv(OUT_MULTI, index=False)

# earliest-ever connection per firm (across all networks)
earliest = (df.sort_values("recorded_date")
              .groupby("name_key", as_index=False)
              .first()[["name_key","firm_name_standardized","recorded_date",
                        "connectivity_type","location_country_iso3"]]
              .rename(columns={"recorded_date":"first_ever_date",
                               "connectivity_type":"first_ever_network"}))

print(f"Total unique firms (by name): {df['name_key'].nunique()}")
print(f"Firms in >1 network type: {len(multi_keys)}")
print(f"\nEarliest-ever connection by network type:")
print(earliest['first_ever_network'].value_counts().to_string())
print(f"\nExample multi-network firms (UUCP -> NSFNET progression):")
sample = multi[multi['name_key'].isin(list(multi_keys)[:8])]
print(sample[['firm_name_standardized','connectivity_type','recorded_date']].to_string())
print(f"\nWrote {OUT_TIMELINE} and {OUT_MULTI}")