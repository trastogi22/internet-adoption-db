"""
Adoption-over-time visualizations (firms only).
Handles known data artifacts: UUCP 1989-90 snapshot gap, source date windows.
Charts are ANNOTATED so the artifacts aren't read as real adoption patterns.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

FIG = Path("output/figures"); FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/firm_internet_connectivity.csv")
df = df[df["entity_type"] == "firm"].copy()
df["year"] = pd.to_numeric(df["recorded_date"].astype(str).str[:4], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# ---- Chart 1: New firm observations per year, stacked by network ----
pivot = (df.groupby(["year", "connectivity_type"]).size()
           .unstack(fill_value=0).reindex(range(1987, 1995), fill_value=0))

fig, ax = plt.subplots(figsize=(9, 5))
pivot.plot(kind="bar", stacked=True, ax=ax,
           color=["#4C72B0", "#DD8452", "#55A868"])
ax.set_title("Firm connectivity observations per year, by network")
ax.set_xlabel("Year (first observed)")
ax.set_ylabel("Number of firms")
ax.legend(title="Network", fontsize=8)
# Annotate the gap
ax.annotate("UUCP snapshot gap\n(1989-90 missing)",
            xy=(2, 200), xytext=(2, 2500),
            ha="center", fontsize=8, color="red",
            arrowprops=dict(arrowstyle="->", color="red"))
plt.figtext(0.5, -0.02,
            "Caveat: dates = first appearance in source snapshots, not verified "
            "first connection. UUCP 1989-90 missing (sparse snapshots); "
            "NSFNET 1992-94 only.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_network.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_network.png")

# ---- Chart 2: Cumulative firms online (earliest appearance per firm) ----
# earliest year per firm (across networks) to avoid double counting
first = df.groupby("firm_name_standardized")["year"].min()
by_year = first.value_counts().reindex(range(1987, 1995), fill_value=0).sort_index()
cumulative = by_year.cumsum()

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(cumulative.index, cumulative.values, marker="o", linewidth=2)
ax.set_title("Cumulative firms first observed online")
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative unique firms")
# shade the gap
ax.axvspan(1988.5, 1990.5, color="red", alpha=0.08)
ax.annotate("1989-90: UUCP snapshot gap\n(curve understates adoption here)",
            xy=(1989.5, cumulative.get(1989, 0)), xytext=(1989.5, cumulative.max()*0.5),
            ha="center", fontsize=8, color="red",
            arrowprops=dict(arrowstyle="->", color="red"))
plt.figtext(0.5, -0.02,
            "Caveat: 'first observed', not verified first connection. "
            "1989-90 flat due to missing UUCP snapshots, not a real plateau.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_cumulative.png", dpi=150, bbox_inches="tight")
print("Saved adoption_cumulative.png")

# ---- Chart 3: Top countries over time (international dimension) ----
top = df["location_country_iso3"].value_counts().head(6).index
sub = df[df["location_country_iso3"].isin(top)]
cp = (sub.groupby(["year", "location_country_iso3"]).size()
        .unstack(fill_value=0).reindex(range(1987, 1995), fill_value=0))
# Drop USA to see the others (USA dwarfs all)
non_us = [c for c in cp.columns if c != "USA"]

fig, ax = plt.subplots(figsize=(9, 5))
cp[non_us].plot(ax=ax, marker="o")
ax.set_title("Firm observations per year, top non-US countries")
ax.set_xlabel("Year"); ax.set_ylabel("Number of firms")
ax.legend(title="Country", fontsize=8)
plt.figtext(0.5, -0.02,
            "Non-US firms appear mainly via NSFNET (1992+). USA excluded here "
            "(dominates); international coverage begins with NSFNET.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_country.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_country.png")

print("\nSummary:")
print("Cumulative firms by 1993:", int(cumulative.iloc[-1]))
print("Peak new-firm year:", int(by_year.idxmax()), f"({int(by_year.max())} firms)")