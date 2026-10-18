"""Summaries and visualizations of the combined dataset."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # no display needed; save to file
import matplotlib.pyplot as plt

IN = Path("data/clean/first_connection_by_firm.csv")
FIG_DIR = Path("output/figures")
TAB_DIR = Path("output/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(IN)
df["year"] = df["first_connection_date"].astype(str).str[:4]

# --- Table 1: firms per network ---
by_net = df["first_network"].value_counts().rename_axis("network").reset_index(name="firms")
by_net.to_csv(TAB_DIR / "firms_by_network.csv", index=False)
print("Firms by first network:")
print(by_net.to_string(index=False))

# --- Table 2: firms per year ---
by_year = df["year"].value_counts().sort_index().rename_axis("year").reset_index(name="firms")
by_year.to_csv(TAB_DIR / "firms_by_year.csv", index=False)
print("\nFirms by first-connection year:")
print(by_year.to_string(index=False))

# --- Figure 1: firms by year (bar) ---
plt.figure(figsize=(8, 4))
plt.bar(by_year["year"], by_year["firms"])
plt.title("First-connection year (all firms, both sources)")
plt.xlabel("Year"); plt.ylabel("Number of firms")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIG_DIR / "firms_by_year.png", dpi=150)
plt.close()

# --- Figure 2: firms by network (bar) ---
plt.figure(figsize=(5, 4))
plt.bar(by_net["network"], by_net["firms"])
plt.title("Firms by first network")
plt.ylabel("Number of firms")
plt.tight_layout()
plt.savefig(FIG_DIR / "firms_by_network.png", dpi=150)
plt.close()

# --- Table 3: confidence breakdown ---
by_conf = df["confidence"].value_counts(dropna=False).rename_axis("confidence").reset_index(name="firms")
by_conf.to_csv(TAB_DIR / "firms_by_confidence.csv", index=False)
print("\nFirms by confidence:")
print(by_conf.to_string(index=False))

print(f"\nSaved figures to {FIG_DIR}/ and tables to {TAB_DIR}/")