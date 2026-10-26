"""
Download NSFNET-era NANOG monthly mbox archives (gzipped).
Saves raw, unaltered, to data/raw/nsfnet_mbox/.
"""
import time
import calendar
from pathlib import Path
import requests

OUT_DIR = Path("data/raw/nsfnet_mbox")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE = ("https://lists.nanog.org/archives/list/nanog@lists.nanog.org/export/"
        "nanog@lists.nanog.org-{y}-{m:02d}.mbox.gz"
        "?start={y}-{m:02d}-01&end={ey}-{em:02d}-01")

# Months to fetch (PRDB messages are common 1992-1994)
YEARS = range(1992, 1995)      # 1992, 1993, 1994
MONTHS = range(1, 13)

def main():
    for y in YEARS:
        for m in MONTHS:
            # end = first day of next month
            if m == 12:
                ey, em = y + 1, 1
            else:
                ey, em = y, m + 1
            url = BASE.format(y=y, m=m, ey=ey, em=em)
            out = OUT_DIR / f"nanog_{y}_{m:02d}.mbox.gz"
            if out.exists():
                print(f"skip {out.name} (exists)")
                continue
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 0:
                    out.write_bytes(r.content)
                    print(f"saved {out.name} ({len(r.content)} bytes)")
                else:
                    print(f"skip {y}-{m:02d} (status {r.status_code})")
            except Exception as e:
                print(f"error {y}-{m:02d}: {e}")
            time.sleep(1)   # be polite to the server

if __name__ == "__main__":
    main()