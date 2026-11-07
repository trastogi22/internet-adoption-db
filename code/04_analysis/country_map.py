"""
World map of firms by country (choropleth), using ISO3 codes.
Firms only. Saves static PNG + interactive HTML.
"""
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

FIG = Path("output/figures"); FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/firm_internet_connectivity.csv")
df = df[df["entity_type"] == "firm"].copy()

counts = (df["location_country_iso3"].value_counts()
            .rename_axis("iso3").reset_index(name="firms"))

# Regular scale
fig = px.choropleth(
    counts, locations="iso3", color="firms",
    color_continuous_scale="Blues",
    title="Firms by country (1974-1993, firms only)",
    labels={"firms": "Number of firms"})
fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
fig.write_html(str(FIG / "country_map.html"))
try:
    fig.write_image(str(FIG / "country_map.png"), width=1100, height=600, scale=2)
    print("Saved country_map.png and .html")
except Exception as e:
    print("Saved .html only (PNG needs kaleido). Error:", e)

# Log scale (USA dominates; this reveals the international spread)
counts["log_firms"] = np.log10(counts["firms"])
fig2 = px.choropleth(
    counts, locations="iso3", color="log_firms",
    color_continuous_scale="Blues",
    title="Firms by country (log scale, firms only)",
    labels={"log_firms": "log10(firms)"})
fig2.update_layout(margin=dict(l=0, r=0, t=40, b=0))
fig2.write_html(str(FIG / "country_map_log.html"))
try:
    fig2.write_image(str(FIG / "country_map_log.png"), width=1100, height=600, scale=2)
    print("Saved country_map_log.png")
except Exception:
    pass

print("\nTop countries:")
print(counts.head(12).to_string(index=False))