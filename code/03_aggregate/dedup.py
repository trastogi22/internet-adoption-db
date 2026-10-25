"""
Deduplication + the requested statistic.

Method A: name + state clustering (LinkTransformer, per state).
Method B: address matching (normalized exact).
Statistic: of record-pairs that share an address (Method B duplicates),
what share are ALSO in the same name+state cluster (Method A)?

Keeps all rows and adds firm_group_id (hierarchy), per supervisor Q3.
"""
import re
import itertools
from pathlib import Path
import pandas as pd
import linktransformer as lt

IN = Path("data/clean/uucp_clean.csv")
OUT = Path("data/clean/uucp_deduped.csv")
STATS = Path("output/tables/dedup_statistic.txt")

# ---- Config: set TEST_STATE to a state name to test on one state,
#      or None to run all states. Start with testing!
TEST_STATE = None

NAME_THRESHOLD = 0.5   # LinkTransformer cosine threshold (tune later)


def normalize_address(addr):
    s = str(addr).lower()
    s = re.sub(r"[^\w\s]", " ", s)       # strip punctuation
    s = re.sub(r"\b(suite|ste|floor|fl|mailstop|ms|p\s*o\s*box|box)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def cluster_names_per_state(df):
    """Run LinkTransformer name clustering within each state. Returns df with
    a global 'name_state_cluster' id."""
    results = []
    next_id = 0
    for state, g in df.groupby("state"):
        g = g.copy().reset_index(drop=True)
        if len(g) < 2 or not str(state).strip():
            g["local_cluster"] = range(len(g))  # each its own cluster
        else:
            clustered = lt.cluster_rows(
                g, model="all-MiniLM-L6-v2", on=["firm_name_clean"],
                cluster_params={"threshold": NAME_THRESHOLD,
                                "min cluster size": 1, "metric": "cosine"},
            )
            # LinkTransformer adds a cluster column; find it
            cluster_col = [c for c in clustered.columns
                           if "cluster" in c.lower()][-1]
            g["local_cluster"] = clustered[cluster_col].values
        # make cluster ids globally unique
        g["name_state_cluster"] = g["local_cluster"].astype(str) + f"_{state}"
        results.append(g)
    out = pd.concat(results, ignore_index=True)
    # map to integer ids
    out["name_state_cluster"] = out.groupby("name_state_cluster").ngroup()
    return out


def main():
    df = pd.read_csv(IN)
    df["state"] = df["state"].fillna("")
    df["norm_addr"] = df["location_raw"].map(normalize_address)

    if TEST_STATE:
        df = df[df["state"] == TEST_STATE].copy()
        print(f"TEST MODE: {TEST_STATE} only, {len(df)} rows")

    # ---- Method A: name + state clustering ----
    print("Running LinkTransformer name clustering (this may take a minute)...")
    df = cluster_names_per_state(df)
    df["firm_group_id"] = df["name_state_cluster"]  # hierarchy id

    # ---- Method B: address groups (same normalized non-empty address) ----
    # Cap group size: very large groups are shared facilities / gateways
    # (e.g., many unrelated firms behind one UUCP host), NOT true duplicates.
    MAX_ADDR_GROUP = 5
    df["addr_group"] = -1
    valid = df["norm_addr"].str.len() > 5
    tmp = df.loc[valid].copy()
    tmp["g"] = tmp.groupby("norm_addr").ngroup()
    sizes = tmp["g"].map(tmp["g"].value_counts())
    keep = tmp[sizes <= MAX_ADDR_GROUP]
    df.loc[keep.index, "addr_group"] = keep["g"].values
    n_excluded = (sizes > MAX_ADDR_GROUP).sum()
    print(f"Excluded {n_excluded} rows in oversized address groups "
          f"(>{MAX_ADDR_GROUP} members; likely shared facilities).") 

    # ---- The statistic (pair-level) ----
    # Method B duplicate pairs: rows sharing an addr_group (>=2 members)
    b_pairs = set()
    for gid, g in df[df["addr_group"] >= 0].groupby("addr_group"):
        idx = list(g.index)
        if len(idx) >= 2:
            for a, b in itertools.combinations(sorted(idx), 2):
                b_pairs.add((a, b))

    # Of those, how many are ALSO same name+state cluster (Method A)?
    caught_by_name_state = 0
    for a, b in b_pairs:
        if df.loc[a, "name_state_cluster"] == df.loc[b, "name_state_cluster"]:
            caught_by_name_state += 1

    share = (caught_by_name_state / len(b_pairs)) if b_pairs else float("nan")

    # ---- Report ----
    report = (
        f"=== Deduplication statistic ===\n"
        f"Scope: {'TEST ('+TEST_STATE+')' if TEST_STATE else 'all states'}\n"
        f"Rows: {len(df)}\n"
        f"Address-duplicate pairs (Method B): {len(b_pairs)}\n"
        f"...of which also caught by name+state (Method A): {caught_by_name_state}\n"
        f"Share already caught by name+state: {share:.1%}\n"
        f"Max address-group size used: {MAX_ADDR_GROUP} "
        f"(larger groups treated as shared facilities, excluded)\n"
    )
    print(report)
    STATS.parent.mkdir(parents=True, exist_ok=True)
    STATS.write_text(report)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} ({len(df)} rows) and {STATS}")


if __name__ == "__main__":
    main()