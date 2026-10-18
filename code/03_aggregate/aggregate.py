"""
Aggregate all cleaned sources into one dataset.
- Stacks source files with a common schema.
- Standardizes names for matching; assigns firm_id.
- Derives first_connection per firm across networks.
"""
import re
from pathlib import Path
import pandas as pd

CLEAN_DIR = Path("data/clean")
SOURCES = ["ietf_clean.csv", "uucp_clean.csv"]

OUT_ALL = Path("data/clean/combined_observations.csv")
OUT_FIRST = Path("data/clean/first_connection_by_firm.csv")

SUFFIXES = (r"\b(inc|incorporated|corp|corporation|co|company|ltd|llc|lp|"
            r"plc|gmbh|ag|sa|srl|bv|nv)\b\.?")

def standardize(name):
    s = str(name).lower()
    s = re.sub(r"[.,;/()]", " ", s)      # punctuation -> space
    s = re.sub(SUFFIXES, " ", s)         # drop legal suffixes
    s = re.sub(r"\s+", " ", s).strip()   # collapse spaces
    return s

# Load and stack
frames = []
for fn in SOURCES:
    p = CLEAN_DIR / fn
    if p.exists():
        frames.append(pd.read_csv(p))
        print(f"Loaded {fn}: {len(frames[-1])} rows")
    else:
        print(f"WARNING: {fn} not found, skipping")

df = pd.concat(frames, ignore_index=True)
print(f"Combined: {len(df)} observations")

# Standardized key for matching
df["match_key"] = df["firm_name_clean"].map(standardize)
df = df[df["match_key"] != ""]

# Assign firm_id by match_key
df["firm_id"] = df.groupby("match_key").ngroup()

# How many firms appear in >1 network?
nets_per_firm = df.groupby("firm_id")["network"].nunique()
multi = (nets_per_firm > 1).sum()
print(f"Unique firms (by match_key): {df['firm_id'].nunique()}")
print(f"Firms appearing in >1 network: {multi}")

# Save all observations
df.to_csv(OUT_ALL, index=False)

# Derive first connection per firm (earliest date)
df_sorted = df.sort_values("connection_date")
first = df_sorted.drop_duplicates(subset=["firm_id"], keep="first").copy()
first = first[["firm_id","firm_name_clean","connection_date","network",
               "network_category","city","state","country","source",
               "confidence","notes"]]
first = first.rename(columns={"connection_date": "first_connection_date",
                              "network": "first_network"})
first.to_csv(OUT_FIRST, index=False)
print(f"\nWrote {OUT_ALL.name} ({len(df)} rows) and "
      f"{OUT_FIRST.name} ({len(first)} firms)")

# Show any cross-source matches (firms in both IETF and UUCP)
cross = df.groupby("firm_id").filter(lambda g: g["source"].nunique() > 1)
if len(cross):
    print("\nFirms observed in multiple sources:")
    print(cross[["firm_name_clean","network","connection_date","source"]]
          .sort_values("firm_name_clean").to_string())
else:
    print("\nNo firms matched across both sources (expected: little overlap).")