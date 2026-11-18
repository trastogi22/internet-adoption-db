"""Bulk-download Internet Monthly Reports (1988-1996) from history.rfc-editor.org.
Files are named imr[YYMM].txt. Saves to data/raw/ietf_monthly_reports/."""
import urllib.request
from pathlib import Path

OUT = Path("data/raw/ietf_monthly_reports"); OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://history.rfc-editor.org/imr/imr{yy}{mm}.txt"

got = 0
for yy in range(88, 97):          # 1988-1996
    for mm in range(1, 13):
        url = BASE.format(yy=f"{yy:02d}", mm=f"{mm:02d}")
        dest = OUT / f"imr_19{yy:02d}_{mm:02d}.txt"
        try:
            urllib.request.urlretrieve(url, dest)
            # skip if it's an HTML error page
            head = dest.read_text(errors="ignore")[:200].lower()
            if "<!doctype html" in head or "404" in head[:20]:
                dest.unlink(missing_ok=True)
                continue
            got += 1
        except Exception:
            pass
print(f"Downloaded {got} Internet Monthly Reports to {OUT}")
