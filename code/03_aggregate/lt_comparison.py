"""
Does LinkTransformer add value over exact-normalized matching for
cross-source firm linking? Compare merge counts.
"""
import re
import pandas as pd
import linktransformer as lt

df = pd.read_csv("data/clean/firm_internet_connectivity.csv")

def norm(s):
    s = str(s).lower()
    s = re.sub(r"[.,;/()]", " ", s)
    s = re.sub(r"\b(inc|incorporated|corp|corporation|co|company|ltd|llc|"
               r"gmbh|ag|sa)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()

df["norm_key"] = df["firm_name_standardized"].map(norm)

# Work on UNIQUE normalized names (so LT only works on what norm didn't merge)
uniq = (df[["firm_name_standardized", "norm_key", "location_country_iso3"]]
        .drop_duplicates(subset=["norm_key"]).reset_index(drop=True))
print(f"Unique firms after normalization: {len(uniq)}")

# Run LinkTransformer per country (blocking), count additional merges
results = []
for country, g in uniq.groupby("location_country_iso3"):
    g = g.reset_index(drop=True)
    if len(g) < 2:
        g["lt_cluster"] = range(len(g))
    else:
        out = lt.cluster_rows(
            g, model="all-MiniLM-L6-v2", on=["norm_key"],
            cluster_type="agglomerative",
            cluster_params={"threshold": 0.1,
                            "clustering linkage": "average",
                            "metric": "cosine"})
        col = [c for c in out.columns if "cluster" in c.lower()][-1]
        g["lt_cluster"] = out[col].values
    g["lt_cluster"] = g["lt_cluster"].astype(str) + "_" + str(country)
    results.append(g)

allc = pd.concat(results, ignore_index=True)
allc["lt_cluster"] = allc.groupby("lt_cluster").ngroup()

n_norm = len(uniq)                      # firms after normalization
n_lt = allc["lt_cluster"].nunique()     # firms after LT on top
print(f"Firms after LinkTransformer (on top of norm): {n_lt}")
print(f"Additional merges from LinkTransformer: {n_norm - n_lt}")
print(f"  (= {(n_norm - n_lt)/n_norm*100:.1f}% further reduction)")

# Show examples of what LT merged that norm didn't
merged = allc.groupby("lt_cluster").filter(lambda x: len(x) > 1)
print("\nExamples of LinkTransformer merges (beyond normalization):")
for cid, grp in list(merged.groupby("lt_cluster"))[:15]:
    names = grp["firm_name_standardized"].tolist()
    print(" | ".join(names))