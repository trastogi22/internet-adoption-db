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

COUNTRY_ISO3 = {"USA": "USA"}  # already USA; extend if non-US added

# Map our event_type/source to their controlled vocab
def map_event_type(row):
    src = row.get("source", "")
    et = str(row.get("event_type", ""))
    if src == "ietf_imr":
        return "operational_start_reported"
    if src == "uucp_map":
        return "map_appearance_observed"
    return et

def map_connectivity_type(row):
    src = row.get("source", "")
    if src == "ietf_imr":
        return "Internet access"
    if src == "uucp_map":
        return "UUCP mail"
    return "unknown"

df = pd.read_csv(IN)

out = pd.DataFrame()
out["firm_name_raw"] = df["firm_name_raw"]
out["firm_name_standardized"] = df["firm_name_clean"]
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
cols = ["firm_name_raw","firm_name_standardized","network_name",
        "connectivity_type","recorded_date","event_type",
        "location_city","location_region","location_country_iso3",
        "location_address_raw","location_type","first_connection_status",
        "source_url_1","source_url_2","source_url_3","evidence","notes"]
out = out.reindex(columns=cols)

OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT, index=False)
print(f"Wrote {len(out)} rows to {OUT} in target schema.")
print(out.head(10).to_string())