"""
Extract 'Additions to the NSFNET ... routing database' messages from the
downloaded NANOG mbox archives. Writes each message body as a .txt into
data/raw/nsfnet_prdb/ so the existing clean_nsfnet.py parser can process them.
"""
import gzip
import mailbox
import tempfile
import os
import re
from pathlib import Path

MBOX_DIR = Path("data/raw/nsfnet_mbox")
OUT_DIR = Path("data/raw/nsfnet_prdb")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def is_prdb_addition(subject):
    s = subject.lower()
    # must look like an "additions ... nsfnet ... database" message
    has_add = ("addition" in s) or ("addtition" in s)  # include the typo
    has_nsfnet = "nsfnet" in s
    has_db = "database" in s
    # exclude non-data messages
    bad = any(w in s for w in ["re:", "postpone", "correction", "report",
                               "minutes", "survey", "past"])
    return has_add and has_nsfnet and has_db and not bad

def get_body(msg):
    """Return the plain-text body of an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(
                        "utf-8", errors="ignore")
                except Exception:
                    return part.get_payload()
        return ""
    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode("utf-8", errors="ignore")
    return str(msg.get_payload())

def main():
    count = 0
    for f in sorted(MBOX_DIR.glob("*.mbox.gz")):
        # filename like nanog_1992_03.mbox.gz -> year, month
        m = re.search(r"(\d{4})_(\d{2})", f.name)
        ym = f"{m.group(1)}_{m.group(2)}" if m else "unknown"

        data = gzip.decompress(f.read_bytes())
        tmp = tempfile.NamedTemporaryFile(suffix=".mbox", delete=False)
        tmp.write(data); tmp.close()
        mb = mailbox.mbox(tmp.name)

        idx = 0
        for msg in mb:
            subj = str(msg.get("subject", ""))
            if is_prdb_addition(subj):
                body = get_body(msg)
                if len(body) < 200:   # skip tiny/empty
                    continue
                idx += 1
                out = OUT_DIR / f"prdb_{ym}_{idx}.txt"
                out.write_text(body, errors="ignore")
                nlines = body.count("\n")
                print(f"{out.name}: {nlines} lines  | {subj.strip()[:60]}")
                count += 1
        os.unlink(tmp.name)
    print(f"\nExtracted {count} PRDB messages to {OUT_DIR}")

if __name__ == "__main__":
    main()