"""
Adoption-over-time visualizations (firms only), full timeline 1974-1993.
Spans ARPANET/DDN (1974-84), UUCP (1987-92), NSFNET (1992-93).
Annotated for data artifacts: UUCP 1989-90 gap, sparse ARPANET years,
non-overlapping source windows.
"""
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

# ---- Chart 1: new firm observations per year, stacked by network ----
pivot = (df.groupby(["year", "connectivity_type"]).size()
           .unstack(fill_value=0).reindex(YEARS, fill_value=0))

fig, ax = plt.subplots(figsize=(11, 5))
pivot.plot(kind="bar", stacked=True, ax=ax,
           color=["#C44E52", "#4C72B0", "#DD8452", "#55A868"])
ax.set_title("Firm connectivity observations per year, by network (1974-1993)")
ax.set_xlabel("Year (first observed)")
ax.set_ylabel("Number of firms")
ax.legend(title="Network", fontsize=8)
plt.figtext(0.5, -0.03,
            "Caveat: dates = first appearance in source snapshots, not verified "
            "first connection. ARPANET sparse years (no snapshot every year); "
            "UUCP 1989-90 missing; sources cover different eras.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_network.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_network.png")

# ---- Chart 2: cumulative firms (earliest appearance per firm) ----
first = df.groupby("firm_name_standardized")["year"].min()
by_year = first.value_counts().reindex(YEARS, fill_value=0).sort_index()
cumulative = by_year.cumsum()

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(cumulative.index, cumulative.values, marker="o", linewidth=2)
ax.set_title("Cumulative firms first observed online (1974-1993)")
ax.set_xlabel("Year"); ax.set_ylabel("Cumulative unique firms")
# shade era boundaries / gaps
ax.axvspan(1984.5, 1986.5, color="gray", alpha=0.08)   # no data 1985-86
ax.axvspan(1988.5, 1990.5, color="red", alpha=0.08)    # UUCP gap
ax.annotate("1985-86: no source coverage", xy=(1985.5, cumulative.get(1984,0)),
            xytext=(1980, cumulative.max()*0.6), fontsize=8, color="gray",
            arrowprops=dict(arrowstyle="->", color="gray"))
ax.annotate("1989-90: UUCP snapshot gap", xy=(1989.5, cumulative.get(1989,0)),
            xytext=(1986, cumulative.max()*0.85), fontsize=8, color="red",
            arrowprops=dict(arrowstyle="->", color="red"))
plt.figtext(0.5, -0.03,
            "Caveat: 'first observed', not verified first connection. Flat/jumpy "
            "segments reflect source coverage (ARPANET snapshots, 1985-86 gap, "
            "UUCP 1989-90 gap), not real adoption pauses.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_cumulative.png", dpi=150, bbox_inches="tight")
print("Saved adoption_cumulative.png")

# ---- Chart 3: top non-US countries over time ----
# ---- Chart 3: Top countries over time, INCLUDING USA (log scale) ----
top = df["location_country_iso3"].value_counts().head(8).index
sub = df[df["location_country_iso3"].isin(top)]
cp = (sub.groupby(["year", "location_country_iso3"]).size()
        .unstack(fill_value=0).reindex(range(1974, 1995), fill_value=0))

fig, ax = plt.subplots(figsize=(11, 5))
cp.plot(ax=ax, marker="o")                 # includes USA (no filtering)
ax.set_yscale("log")                       # log so USA + small countries both visible
ax.set_title("Firm observations per year by country, incl. USA (log scale)")
ax.set_xlabel("Year"); ax.set_ylabel("Number of firms (log scale)")
ax.legend(title="Country", fontsize=8, ncol=2)
plt.figtext(0.5, -0.02,
            "Log scale so USA (~13,700) and smaller countries are both visible. "
            "International firms appear mainly via NSFNET (1992+). Reflects source "
            "coverage, not a complete global census.",
            ha="center", fontsize=7, style="italic", wrap=True)
plt.tight_layout()
plt.savefig(FIG / "adoption_by_country.png", dpi=150, bbox_inches="tight")
print("Saved adoption_by_country.png (incl USA, log)")