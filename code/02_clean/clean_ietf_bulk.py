"""
Parse Internet Monthly Reports (1988-1996) for new-member firm listings.
Targets structured sections: JvNCnet 'New on-line members', NEARnet 'new members
who joined', PREPnet 'New Members'. Uses filename month as the report date.
High confidence (explicit new-member/operational statements).
"""
import re
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/ietf_monthly_reports")
OUT = Path("data/clean/ietf_bulk_clean.csv")

# Section triggers -> each starts a list of new members
TRIGGERS = [
    re.compile(r"new on-line members", re.I),
    re.compile(r"welcome the following new members", re.I),
    re.compile(r"new members who have\s+joined", re.I),
    re.compile(r"prepnet new members", re.I),
    re.compile(r"new members joined", re.I),
    re.compile(r"new member attachments include", re.I),
]
# Stop a listing when we hit a blank-ish boundary or a new section header
STOP = re.compile(r"^\s*$|^[A-Z][A-Z ]{6,}$|^\s*[A-Z]\.\s|^-{3,}|^\s*\d+\.\s|"
                  r"mini-seminar|update|signed|agreement|page \d+", re.I)

# A plausible firm line: has letters, a comma or ' of ', not too long, not a footer
FIRM_LINE = re.compile(r"^\s{2,}([A-Z][^\n]{3,70})$")
FOOTER = re.compile(r"cooper|internet monthly|page \d+|\[page", re.I)

def month_from_name(fname):
    m = re.search(r"imr_(\d{4})_(\d{2})", fname)
    return f"{m.group(1)}-{m.group(2)}" if m else ""

def parse_firm_location(line):
    """Split 'Firm, City, ST' or 'Firm (ABBR) of City, MA' into name + loc."""
    s = line.strip().rstrip(".")
    # 'Firm of City, ST'
    m = re.match(r"(.+?)\s+of\s+([A-Za-z .'-]+,\s*[A-Z]{2})$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # 'Firm, City, ST'  (last two comma parts = city, state)
    parts = [p.strip() for p in s.split(",")]
    if len(parts) >= 3 and re.match(r"^[A-Z]{2}$", parts[-1]):
        return ", ".join(parts[:-2]).strip(), f"{parts[-2]}, {parts[-1]}"
    if len(parts) == 2 and re.match(r"^[A-Z]{2}$", parts[-1]):
        return parts[0], parts[-1]
    return s, ""   # name only

rows = []
for f in sorted(RAW.glob("imr_*.txt")):
    month = month_from_name(f.name)
    lines = f.read_text(errors="ignore").splitlines()
    i = 0
    while i < len(lines):
        if any(t.search(lines[i]) for t in TRIGGERS):
            trig = lines[i].strip()[:50]
            # scan a window of up to 30 lines after the trigger
            j = i + 1
            blanks = 0
            while j < len(lines) and j < i + 30:
                ln = lines[j]
                # page-break footers: skip WITHOUT counting as list-ending
                if FOOTER.search(ln) or ln.startswith("\f"):
                    blanks = 0
                    j += 1; continue
                if ln.strip() == "":
                    blanks += 1
                    if blanks >= 3:       
                        break
                    j += 1; continue
                blanks = 0
                # hard stop at a new lettered/section header (B., C., LOS NETTOS, etc.)
                if re.match(r"^\s*[A-Z]\.\s+[A-Z]", ln) or re.match(r"^[A-Z][A-Z ]{5,}$", ln.strip()):
                    break
                # candidate firm line: indented, starts with a letter/number+letter
                m = re.match(r"^\s{2,}([A-Za-z0-9].{3,75})$", ln)
                if m:
                    cand = m.group(1).strip()
                    name, loc = parse_firm_location(cand)
                    words = name.split()
                    is_prose = (len(words) > 7 or
                                re.search(r"\b(attended|talked|gave|held|will|also|"
                                          r"presented|participated|signed|expected|agreement|"
                                          r"welcome|during|month|sponsored|jointly|classroom|"
                                          r"databases|resources|communication|telecommunications|"
                                          r"program|seminar|newspaper|periodicals|teachers|information regarding|contact|options|"
                                          r"commonwealth|connectivity)\b", name, re.I) or
                                re.match(r"(the |within |we |while |their |there |all |"
                                         r"assistant |technologies for |\d+\s|[a-z])", name) or
                                re.search(r"@|e-mail|telephone|floor|\bst\.|\broad\b|\bave\b", name, re.I) or
                                re.search(r"\d{3,}", name))      # addresses/phone numbers
                    if len(name) >= 4 and not is_prose:
                        rows.append({
                            "firm_name_raw": name.rstrip(",. "),
                            "location_raw": loc,
                            "report_month": month, "source_file": f.name,
                            "trigger": trig})
                j += 1
            i = j
        else:
            i += 1

df = pd.DataFrame(rows).drop_duplicates(subset=["firm_name_raw", "report_month"])
print(f"Extracted {len(df)} new-member firm-rows from {df['source_file'].nunique()} reports")
print(f"Date range: {df['report_month'].min()} to {df['report_month'].max()}")
print("\nSample:")
print(df[["firm_name_raw", "location_raw", "report_month"]].head(30).to_string())
print("\nBy trigger type:")
print(df["trigger"].value_counts().head().to_string())

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"\nWrote {OUT}")