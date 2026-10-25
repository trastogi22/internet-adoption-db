"""Scan clustering thresholds on California to find a sensible one."""
import pandas as pd
import linktransformer as lt

df = pd.read_csv("data/clean/uucp_clean.csv")
df = df[df["state"].fillna("") == "California"].copy().reset_index(drop=True)
print(f"California rows: {len(df)}")

for thr in [0.05, 0.1, 0.15, 0.2, 0.3]:
    out = lt.cluster_rows(
        df, model="all-MiniLM-L6-v2", on=["firm_name_clean"],
        cluster_type="agglomerative",
        cluster_params={"threshold": thr, "clustering linkage": "average",
                        "metric": "cosine"})
    col = [c for c in out.columns if "cluster" in c.lower()][-1]
    vc = out[col].value_counts()
    print(f"threshold={thr}: groups={out[col].nunique()}, "
          f"largest={vc.max()}, multi-member={ (vc>1).sum() }")