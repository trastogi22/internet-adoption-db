"""Reshape combined dataset into the supervisors' target schema."""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/clean/combined_observations.csv")
OUT = Path("data/clean/firm_internet_connectivity.csv")

# US state abbreviation -> full name (extend as needed)
STATES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
    "CO":"Colorado","CT":"Connecticut","DE":"Delaware","DC":"District of Columbia",
    "FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
    "IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana",
    "ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan",
    "MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey",
    "NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
    "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
    "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota",
    "TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
}

COUNTRY_ISO3 = {"USA":"USA","CAN":"CAN","CHE":"CHE","ITA":"ITA","DEU":"DEU",
                "FRA":"FRA","GBR":"GBR","NLD":"NLD","JPN":"JPN"}

# Map our event_type/source to their controlled vocab
def map_event_type(row):
    src = row.get("source", "")
    et = str(row.get("event_type", ""))
    if src == "ietf_imr":
        return "operational_start_reported"
    if src == "uucp_map":
        return "map_appearance_observed"
    if src == "nsfnet_prdb":
        return "routing_addition_announced"
    return et

def map_connectivity_type(row):
    src = row.get("source", "")
    if src == "ietf_imr":
        return "Internet access"
    if src == "uucp_map":
        return "UUCP mail"
    if src == "nsfnet_prdb":
        return "Internet access (routing record)"
    return "unknown"

df = pd.read_csv(IN)
# Merge in firm_group_id from the dedup output (UUCP rows).
DEDUP = Path("data/clean/uucp_deduped.csv")
if DEDUP.exists():
    dd = pd.read_csv(DEDUP)[["firm_name_raw", "state", "firm_group_id"]]
    dd = dd.drop_duplicates(subset=["firm_name_raw", "state"])
    df = df.merge(dd, on=["firm_name_raw", "state"], how="left")
else:
    df["firm_group_id"] = pd.NA

# IETF rows and any unmatched UUCP rows get their own unique group ids,
# continuing numbering after the existing max.
existing_max = df["firm_group_id"].max()
start = int(existing_max) + 1 if pd.notna(existing_max) else 0
missing = df["firm_group_id"].isna()
df.loc[missing, "firm_group_id"] = range(start, start + missing.sum())
df["firm_group_id"] = df["firm_group_id"].astype(int)

out = pd.DataFrame()
out["firm_name_raw"] = df["firm_name_raw"]
out["firm_name_standardized"] = df["firm_name_clean"]
out["firm_group_id"] = df["firm_group_id"].values
out["network_name"] = df["network"]
out["connectivity_type"] = df.apply(map_connectivity_type, axis=1)
out["recorded_date"] = df["connection_date"]
out["event_type"] = df.apply(map_event_type, axis=1)
out["location_city"] = df["city"].fillna("")
out["location_region"] = df["state"].fillna("").map(
    lambda s: STATES.get(str(s).strip(), str(s)))
out["location_country_iso3"] = df["country"].fillna("USA").map(
    lambda c: COUNTRY_ISO3.get(str(c).strip(), str(c)))
out["location_address_raw"] = df["location_raw"].fillna("")
out["location_type"] = "unspecified"
# We have NOT verified any of these are the true first connection:
out["first_connection_status"] = "not_established"
out["source_url_1"] = df["source_url"]
out["source_url_2"] = ""
out["source_url_3"] = ""
out["evidence"] = df["source_quote"].fillna("")
out["notes"] = df["notes"].fillna("")

# Column order exactly matching their example
cols = ["firm_name_raw","firm_name_standardized","firm_group_id","network_name",
        "connectivity_type","recorded_date","event_type",
        "location_city","location_region","location_country_iso3",
        "location_address_raw","location_type","first_connection_status",
        "source_url_1","source_url_2","source_url_3","evidence","notes"]
out = out.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT, index=False)
print(f"Wrote {len(out)} rows to {OUT} in target schema.")
print(out.head(10).to_string())