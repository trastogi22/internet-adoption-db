"""
Sample funnel: documents raw -> clean counts per source, and final
entity_type composition. Answers 'what is the starting/clean sample and
what is lost at each step.'
"""
import pandas as pd
from pathlib import Path

def count(f):
    p = Path(f)
    return len(pd.read_csv(p)) if p.exists() else None

# Stage counts (raw/interim/clean) per source
rows = [
    # source, raw, after_parse, final_clean, notes
    ("ARPANET/DDN", 33220, 33220, count("data/clean/arpanet_clean.csv"),
     "people-rows -> unique orgs; earliest across 7 snapshots (1974-84); junk filtered"),
    ("UUCP mail", count("data/interim/uucp_candidates.csv"),
     count("data/interim/uucp_candidates.csv"), count("data/clean/uucp_clean.csv"),
     "monthly maps; same node repeats -> earliest appearance; non-firms filtered"),
    ("NSFNET", count("data/interim/nsfnet_candidates.csv"),
     count("data/interim/nsfnet_candidates.csv"), count("data/clean/nsfnet_clean.csv"),
     "weekly messages; repeats -> earliest appearance per network"),
    ("IETF", 108, 353, count("data/clean/ietf_clean.csv"),
     "108 Monthly Reports -> new-member sections parsed -> dedup to unique firms"),
]

print("="*90)
print("SAMPLE FUNNEL: raw -> clean, per source")
print("="*90)
print(f"{'Source':<16}{'Raw':>10}{'Parsed':>10}{'Final':>10}   What is lost")
print("-"*90)
for src, raw, parsed, final, note in rows:
    r = f"{raw:,}" if raw else "n/a"
    p = f"{parsed:,}" if parsed else "n/a"
    fi = f"{final:,}" if final else "n/a"
    print(f"{src:<16}{r:>10}{p:>10}{fi:>10}   {note}")

# Final dataset
df = pd.read_csv("data/clean/firm_internet_connectivity.csv")
print("-"*90)
print(f"{'FINAL TOTAL':<16}{'':>10}{'':>10}{len(df):>10,}")
print()

print("="*90)
print("FINAL COMPOSITION by entity_type")
print("="*90)
et = df["entity_type"].value_counts()
for k, v in et.items():
    print(f"  {k:<16}{v:>8,}")
print(f"  {'TOTAL':<16}{len(df):>8,}")
print(f"\n  Firms only: {et.get('firm',0):,}  "
      f"(non-firm retained-but-filterable: {len(df)-et.get('firm',0):,})")

print()
print("="*90)
print("BY SOURCE x ENTITY_TYPE")
print("="*90)
print(pd.crosstab(df["connectivity_type"], df["entity_type"]))

print()
print("="*90)
print("TIMELINE")
print("="*90)
yr = df["recorded_date"].astype(str).str[:4]
print("Year range:", yr.min(), "-", yr.max())
print("Firms per year:")
f = df[df["entity_type"]=="firm"]
print(f["recorded_date"].astype(str).str[:4].value_counts().sort_index().to_string())