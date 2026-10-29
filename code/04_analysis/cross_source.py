"""
Cross-source firm linking with LinkTransformer (threshold 0.1, per country).
Assigns a cross-source global_firm_id, recomputes multi-network firms and the
UUCP->NSFNET timing finding. Compares against exact-normalized matching.
"""
import re
from pathlib import Path
import pandas as pd
import linktransformer as lt

IN = Path("data/clean/firm_internet_connectivity.csv")
OUT_TIMELINE = Path("data/clean/firm_network_timeline.csv")
OUT_MULTI = Path("output/tables/multi_network_firms.csv")
TAB = Path("output/tables"); TAB.mkdir(parents=True, exist_ok=True)

SUFFIX = (r"\b(inc|incorporated|corp|corporation|co|company|ltd|llc|lp|plc|"
          r"gmbh|ag|sa|srl|bv|nv)\b\.?")

def norm(s):
    s = str(s).lower()
    s = re.sub(r"[.,;/()]", " ", s)
    s = re.sub(SUFFIX, " ", s)
    return re.sub(r"\s+", " ", s).strip()

df = pd.read_csv(IN)
df["norm_key"] = df["firm_name_standardized"].map(norm)
df = df[df["norm_key"] != ""].copy()
df["country"] = df["location_country_iso3"].fillna("USA")

# ---- Baseline: exact-normalized matching ----
exact_firms = df["norm_key"].nunique()

# ---- LinkTransformer linking (0.1, blocked by country) ----
uniq = df[["norm_key", "country"]].drop_duplicates("norm_key").reset_index(drop=True)
parts = []
for country, g in uniq.groupby("country"):
    g = g.reset_index(drop=True)
    if len(g) < 2:
        g["cl"] = range(len(g))
    else:
        out = lt.cluster_rows(
            g, model="all-MiniLM-L6-v2", on=["norm_key"],
            cluster_type="agglomerative",
            cluster_params={"threshold": 0.1,
                            "clustering linkage": "average",
                            "metric": "cosine"})
        col = [c for c in out.columns if "cluster" in c.lower()][-1]
        g["cl"] = out[col].values
    g["cl"] = g["cl"].astype(str) + "_" + str(country)
    parts.append(g)

keymap = pd.concat(parts, ignore_index=True)
keymap["global_firm_id"] = keymap.groupby("cl").ngroup()
key2gid = dict(zip(keymap["norm_key"], keymap["global_firm_id"]))
df["global_firm_id"] = df["norm_key"].map(key2gid)

lt_firms = df["global_firm_id"].nunique()
print(f"Unique firms (exact-normalized): {exact_firms}")
print(f"Unique firms (LinkTransformer 0.1): {lt_firms}")
print(f"Additional merges from LT: {exact_firms - lt_firms}")

# ---- Validation: largest LT clusters (watch for over-merge) ----
vc = df.drop_duplicates("norm_key")["global_firm_id"].value_counts()
print(f"\nLargest firm groups (should be small/coherent):")
for gid in vc.head(5).index:
    names = df[df["global_firm_id"]==gid]["firm_name_standardized"].unique()[:6]
    print(f"  [{len(df[df['global_firm_id']==gid]['norm_key'].unique())}] " +
          " | ".join(names))

# ---- Timeline per firm per network (using global_firm_id) ----
timeline = (df.sort_values("recorded_date")
              .groupby(["global_firm_id", "connectivity_type"], as_index=False)
              .first()[["global_firm_id","firm_name_standardized",
                        "connectivity_type","recorded_date","country"]])
timeline.to_csv(OUT_TIMELINE, index=False)

# ---- Multi-network firms ----
net_counts = df.groupby("global_firm_id")["connectivity_type"].nunique()
multi_ids = net_counts[net_counts > 1].index
multi = timeline[timeline["global_firm_id"].isin(multi_ids)].sort_values(
    ["global_firm_id","recorded_date"])
multi.to_csv(OUT_MULTI, index=False)
print(f"\nFirms in >1 network type: {len(multi_ids)}")

# ---- The UUCP -> NSFNET finding ----
piv = multi.pivot_table(index="global_firm_id", columns="connectivity_type",
                        values="recorded_date", aggfunc="first")
U, N = "UUCP mail", "Internet access (routing record)"
if U in piv and N in piv:
    both = piv.dropna(subset=[U, N])
    gap = (pd.to_datetime(both[N]) - pd.to_datetime(both[U])).dt.days / 365.25
    print(f"\nFirms with both UUCP + NSFNET: {len(both)}")
    print(f"% UUCP first: {(gap>0).mean()*100:.1f}%")
    print(f"Median years UUCP->NSFNET: {gap.median():.1f}")
    print(f"Mean years: {gap.mean():.1f}")

print(f"\nWrote {OUT_TIMELINE} and {OUT_MULTI}")