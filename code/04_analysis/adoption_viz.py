"""Adoption-over-time visualizations (firms only), 1974-1993."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

FIG = Path("output/figures"); FIG.mkdir(parents=True, exist_ok=True)
YEARS = range(1974, 1995)

df = pd.read_csv("data/clean/firm_internet_connectivity.csv")
df = df[df["entity_type"] == "firm"].copy()
df["year"] = pd.to_numeric(df["recorded_date"].astype(str).str[:4], errors="coerce")
df = df.dropna(subset=["year"]); df["year"] = df["year"].astype(int)

# Chart 1: by network (stacked)
pivot = (df.groupby(["year", "connectivity_type"]).size()
           .unstack(fill_value=0).reindex(YEARS, fill_value=0))
fig, ax = plt.subplots(figsize=(11, 5))
pivot.plot(kind="bar", stacked=True, ax=ax)
ax.set_title("Firm observations per year, by network (1974-1993)")
ax.set_xlabel("Year"); ax.set_ylabel("Number of firms")
ax.legend(title="Network", fontsize=8)
plt.figtext(0.5, -0.03,
            "Dates = first appearance in source snapshots, not verified first "
            "connection. ARPANET sparse years; UUCP 1989-90 missing; "
            "sources cover different eras.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_network.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_network.png")

# Chart 2: cumulative
first = df.groupby("firm_name_standardized")["year"].min()
by_year = first.value_counts().reindex(YEARS, fill_value=0).sort_index()
cumulative = by_year.cumsum()
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(cumulative.index, cumulative.values, marker="o", linewidth=2)
ax.set_title("Cumulative firms first observed online (1974-1993)")
ax.set_xlabel("Year"); ax.set_ylabel("Cumulative unique firms")
ax.axvspan(1984.5, 1986.5, color="gray", alpha=0.08)
ax.axvspan(1988.5, 1990.5, color="red", alpha=0.08)
plt.figtext(0.5, -0.03,
            "'First observed', not verified first connection. Flat segments "
            "reflect source coverage (1985-86 gap, UUCP 1989-90 gap), "
            "not real adoption pauses.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_cumulative.png", dpi=150, bbox_inches="tight")
print("Saved adoption_cumulative.png")

# Chart 3: TWO PANELS - USA (left) vs non-US (right)
top = df["location_country_iso3"].value_counts().head(8).index
sub = df[df["location_country_iso3"].isin(top)]
cp = (sub.groupby(["year", "location_country_iso3"]).size()
        .unstack(fill_value=0).reindex(YEARS, fill_value=0))
non_us = [c for c in cp.columns if c != "USA"]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5))
if "USA" in cp:
    axL.plot(cp.index, cp["USA"], marker="o", color="#4C72B0", linewidth=2)
axL.set_title("USA firms per year")
axL.set_xlabel("Year"); axL.set_ylabel("Number of firms")

cp[non_us].plot(ax=axR, marker="o")
axR.set_title("Top non-US countries per year")
axR.set_xlabel("Year"); axR.set_ylabel("Number of firms")
axR.legend(title="Country", fontsize=8)

fig.suptitle("Firm observations per year: USA vs. other countries (1974-1993)")
plt.figtext(0.5, -0.03,
            "USA shown separately (dominates, ~13,700 firms). International firms "
            "appear mainly via NSFNET (1992+). Reflects source coverage, "
            "not a complete global census.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_country.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_country.png TWO_PANEL_v3")
