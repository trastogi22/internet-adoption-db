"""
Classify each row's entity_type: school / military / government /
infrastructure / firm / other. Precedence order matters (first match wins).
Handles known traps (Ameritech != infrastructure, Federal Express != gov,
ITT/TRW Defense divisions = firm, national labs = other).
"""
import re
from pathlib import Path
import pandas as pd

IN = Path("data/clean/firm_internet_connectivity.csv")
OUT = IN  # overwrite in place (adds entity_type column)

name = lambda df: df["firm_name_standardized"].fillna("").astype(str)

# --- SCHOOL ---
SCHOOL = re.compile(
    r"\b(universit(y|ies|aet|a|e)|universid(ad|ade)|college|colleges|"
    r"community college|fachhochschule|hochschule|polytechnic|conservatoire|"
    r"institute of technolog|school of|faculty of)\b", re.I)

# --- MILITARY --- (armed forces units/labs; NOT company 'Defense' divisions)
MILITARY = re.compile(
    r"\b(u\.?\s?s\.?\s?army|u\.?\s?s\.?\s?navy|\bnavy\b|naval|air force|"
    r"marine corps|signal (battalion|brigade)|army (corps|institute|"
    r"ballistic|construction|medical|artificial)|"
    r"strategic defense initiative|defense logistics agency|"
    r"defense contract administration|naval (ocean|sea|research|academy)|"
    r"letterman army|ballistic research|military electronics|"
    r"\bapo\b|armed forces)\b", re.I)

# --- NATIONAL LABS --> 'other' per instruction ---
NATLAB = re.compile(
    r"\b(los alamos|sandia|lawrence livermore|lawrence berkeley|"
    r"oak ridge|argonne|brookhaven|national laborator|national labs)\b", re.I)

# --- INFRASTRUCTURE --- (networks/NICs/backbones/exchanges)
INFRA = re.compile(
    r"\b(ans-cix|ans-reston|\bans\b network|cix\b|backbone|"
    r"regional network|network information cent(er|re)|"
    r"\bnic\b|internet exchange|fix-(east|west)|merit computer network|"
    r"eunet|backbone cabal|network organization)\b", re.I)

# --- GOVERNMENT --- (agencies; NOT Federal Express)
GOVERNMENT = re.compile(
    r"\b(nasa\b|u\.?s\.? geological|usda|federal reserve|"
    r"bureau of standards|national bureau|geological survey|"
    r"department of (energy|defense|agriculture|commerce|water|"
    r"transportation|health|the interior)|"
    r"\bdoe\b|\bdod\b|u\.?s\.? government|federal aviation|"
    r"environmental protection|census bureau|"
    r"los alamos|sandia|lawrence livermore|lawrence berkeley|"
    r"oak ridge|argonne|brookhaven|national laborator|national labs|"
    r"national institutes? of health|\bnih\b|"
    r"centers for disease|federal judicial|federal judical|"  # note the typo variant
    r"city of |county of |state of |"
    r"veterans administration|postal service|"
    r"institute for defense analyses)\b", re.I)

# Exclusions: names that LOOK like a category but are firms
FIRM_OVERRIDE = re.compile(
    r"\b(ameritech|ameritec|federal express|fedex|"
    r"itt defense|trw (military|electronics and defense|defense))\b", re.I)


def classify(nm):
    n = str(nm)
    # Firm overrides win outright (known false positives)
    if FIRM_OVERRIDE.search(n):
        return "firm"
    if SCHOOL.search(n):
        return "school"
    if MILITARY.search(n):
        return "military"
    if INFRA.search(n):
        return "infrastructure"
    if GOVERNMENT.search(n):
        return "government"
    return "firm"               # default


df = pd.read_csv(IN)
df["entity_type"] = name(df).map(classify)
df.to_csv(OUT, index=False)

print("entity_type counts:")
print(df["entity_type"].value_counts().to_string())
print()
# Show samples per category for verification
for cat in ["infrastructure","military","government","school","other"]:
    sub = df[df["entity_type"]==cat]["firm_name_standardized"].drop_duplicates()
    print(f"--- {cat} ({len(sub)}) ---")
    print(sub.head(8).to_string())
    print()