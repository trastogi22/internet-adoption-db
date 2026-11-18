"""Finalize IETF Monthly Report new-member firms into project schema."""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/clean/ietf_bulk_clean.csv")
OUT = Path("data/clean/ietf_clean.csv")   # replaces the old 9-row file

df = pd.read_csv(IN)

def split_loc(loc):
    s = str(loc).strip()
    m = re.match(r"(.+),\s*([A-Z]{2})$", s)
    if m:
        return m.group(1).strip(), m.group(2)
    return "", (s if re.match(r"^[A-Z]{2}$", s) else "")

df[["city","state"]] = df["location_raw"].apply(lambda x: pd.Series(split_loc(x)))
df["firm_name_raw"] = df["firm_name_raw"].str.strip().str.rstrip(",. ")
df["firm_name_clean"] = df["firm_name_raw"]
df["network"] = "Regional IP (IETF IMR)"
df["network_category"] = "Regional IP network membership"
df["connection_date"] = df["report_month"]
df["date_precision"] = "month"
df["event_type"] = "new_member_operational"
df["country"] = "USA"   # IMRs here are US regional networks
df["source"] = "ietf_imr"
df["source_url"] = "https://history.rfc-editor.org/imr/"
df["source_quote"] = df["firm_name_raw"] + " (" + df["report_month"].astype(str) + ")"
df["confidence"] = "high"
df["notes"] = ("new member / fully-operational listing in Internet Monthly Report "
               + df["report_month"].astype(str) + "; regional network (" + df["source_file"] + ")")
df = df[~df["firm_name_raw"].str.contains(r"which was|held in|technologies for the", case=False, na=False)]

# dedup: same firm -> earliest report month
df = df.sort_values("report_month").drop_duplicates(subset=["firm_name_clean"], keep="first")

cols = ["firm_name_raw","firm_name_clean","network","network_category",
        "connection_date","date_precision","event_type","location_raw",
        "city","state","country","source","source_url","source_quote",
        "confidence","notes"]
out = df.reindex(columns=cols)
out.to_csv(OUT, index=False)
print(f"Wrote {OUT}: {len(out)} unique IETF member-firms")
print("Date range:", out["connection_date"].min(), "to", out["connection_date"].max())
print(out[["firm_name_clean","city","state","connection_date"]].head(15).to_string())