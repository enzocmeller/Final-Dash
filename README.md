# 🌽 US Corn Statistics Dashboard

A self-contained, firewall-friendly dashboard that tracks corn statistics for
every US state. One Python script gathers live data and regenerates a single
`index.html` you can open in any browser — **no install, no server, no internet
needed to view it.**

## What it shows
Opens on a **national "United States" overview**; pick any state from the map or
dropdown. A row of **at-a-glance KPI cards** summarizes the current selection.
The dashboard has two tabs.

**Current Conditions tab:**
1. **US map / state selector** — click a state; shade the map by **production share**, **G+E condition**, **NDVI vs normal**, **ECMWF temp/precip anomaly**, **corn stress index**, or **root-zone soil moisture**
2. **Corn Impact Now** — a **corn stress index** combining next-10-day ECMWF heat (wt 10), rain (wt 8) & soil moisture (wt 7), scaled by growth-stage sensitivity; favorable↔stressed with a per-driver read
3. **Soil moisture** — headline **USDA topsoil-moisture status** (Surplus / Adequate / Short, from the weekly NASS farmer survey — the ground-truth wet/dry signal), plus the **ECMWF root-zone** volumetric % as a 10-day outlook (click a state for its soil-moisture forecast)
4. **Phenology table** — Planted / Silking / Dough / Mature / Harvested (% complete) **vs the 5-yr same-week average** (click a stage for its multi-year chart + expected pace)
5. **US-level maps** (national view) — G+E by state, G+E weekly change, and silking by state
6. **US production share & rank** — each state's % of total US corn, as a leaderboard
7. **Acreage & utilization** — planted vs harvested-for-grain acres by year (production = yield × acres)
8. **Price received** — USDA monthly $/bu survey (~2-month lag; context, not a live quote)
9. **Grain stocks** — quarterly USDA on-farm + off-farm corn stocks
10. **Crop quality donut** — E / G / F / P / VP with **G+E** in the center, plus a condition table and the **Crop Condition Index (CCI 1–5)**
11. **CCI / G+E condition evolution** for the season vs. the prior-years range
12. **Yield curve + trend line** (USDA survey, bu/acre) with detrended +/- bars; the **2026 estimate** is shown as a weather-blind share-model baseline (US anchor × state share), not a USDA state number
13. **Weather anomaly** — precip & temperature vs. normal for lead times **1-5 / 6-10 / 11-15 / 1-10 days**, switchable between **GFS (American)** and **ECMWF (European)**, plus a pollination heat-stress count and a **NOAA CPC 8-14 day outlook** pop-up
14. **Growing degree days** — cumulative corn GDD (base 50 °F) vs. the multi-year normal
15. **Satellite NDVI** (NASA Harvest GLAM, corn-masked) — multi-year evolution band + bold current year, plus a deviation-from-normal strip
16. **Observed climate** — Jun–Sep precip & mean temp this season vs. the 1991–2020 normal

**Desk Forecast tab:** an editable **2026/27 US corn crop forecast table** — enter your own state yields, compare to the USDA-tied baseline, save revisions, and export to Excel/CSV.

## Requirements
- **Python 3.10 or newer** (3.12+ recommended). Check with `python --version`.
- That's it. **No third-party packages** — only the Python standard library.
  (Trend & correlation use the built-in `statistics` module, so there is nothing
  to `pip install` and nothing for a firewall to block.)

## One-time setup
1. **Get a free USDA NASS key** (instant, emailed) at
   <https://quickstats.nass.usda.gov/api>.
2. Copy `config.example.json` → **`config.json`** and paste your key into
   `"nass_api_key"`. (`config.json` is gitignored — your key stays local.)
3. *(Optional but recommended on a new work machine)* test connectivity:
   ```
   python src/check_connectivity.py
   ```

## Run / update
Double-click **`run.bat`** (or run `python src/update.py`), then open
`index.html`. Re-run any time to refresh — that's the auto-update.

- **First run** is slower (it builds the 30-year climate normals and the NDVI
  history, then caches them). **Later runs are fast** — only new data is fetched.
- **Changed only the look** (template/CSS in `templates/dashboard.html`)? Rebuild
  the HTML instantly from the last data snapshot, with no network calls:
  ```
  python src/update.py --rebuild
  ```

## Firewall / IT notes
During a **build** (`run.bat`), the tool only ever makes **HTTPS (port 443) GET
requests** to these hosts — viewers of the finished `index.html` need no network
at all. Ask IT to allowlist them if anything is blocked:

| Host | Purpose | Key? |
|------|---------|------|
| `quickstats.nass.usda.gov` | USDA crop data | free key |
| `api.open-meteo.com` | weather forecast / soil moisture | none |
| `archive-api.open-meteo.com` | ERA5 climate normals | none |
| `api.glamdata.org` | GLAM NDVI | none |
| `www.cpc.ncep.noaa.gov` | NOAA CPC 8-14 day outlook maps + discussion — **build-time only**, base64-inlined into `index.html`; if blocked, the last good outlook is carried forward and viewing never calls it | none |
| `glam1.gsfc.nasa.gov` | GLAM alt host — probed by check_connectivity.py only; not used at runtime | none |

**Behind a TLS-intercepting proxy?** If you get `CERTIFICATE_VERIFY_FAILED`,
set `"ca_bundle"` in `config.json` to your corporate root-CA `.pem` file (or set
the `SSL_CERT_FILE` environment variable). Standard `HTTP(S)_PROXY` environment
variables are honored automatically.

## Configuration (`config.json`)
| Key | Default | Meaning |
|-----|---------|---------|
| `nass_api_key` | — | **required** USDA key |
| `states` | `"all"` | `"all"` or a list like `["IA","IL","NE"]` |
| `yield_start_year` | `1990` | first year of the yield/trend series |
| `condition_history_years` | `12` | years of history for the G+E bands & correlation |
| `ndvi_product` | `vnp09h1-ndvi` | GLAM product (VIIRS 8-day); `mod13q1-ndvi` = MODIS 16-day |
| `ndvi_season_start_month` | `4` | season start for the NDVI series |
| `ndvi_baseline_years` | `2` | prior years averaged into the NDVI "standard" / deviation (`0` = none, faster first build) |
| `ndvi_evolution_years` | `3` | recent NDVI seasons overlaid on the evolution chart |
| `ndvi_band_years` | `10` | years in the NDVI min–max band + mean |
| `ndvi_max_composites` | `24` | cap on NDVI points per state |
| `usda_us_yield_seed` | `183.0` | **pre-August US-yield anchor** (bu/ac) from the latest WASDE trend; every state's 2026 estimate ties to it. Auto-replaced by the USDA NASS national yield from ~Aug 12 — update this before August |
| `gdd_start_month` | `1` | month GDD accumulation starts (`1` = January, for the year-round chart) |
| `gdd_evolution_years` | `3` | recent GDD seasons overlaid on the chart |
| `regression_start_year` | `2008` | first training year for the internal yield model (trend extrapolation) |
| `top_counties_for_centroid` | `15` | counties used for the production-weighted corn point |
| `request_delay_seconds` | `0.3` | politeness delay between API calls |
| `request_timeout_seconds` | `60` | per-request HTTP timeout |
| `request_retries` | `3` | retries per failed request |
| `ca_bundle` | `""` | optional corporate root-CA path |

## How it works
```
run.bat → python src/update.py
            ├─ src/sources/nass.py        USDA: progress, condition, yield, county production
            ├─ src/geo/corn_points.py     production-weighted lat/lon per state (bundled county centroids)
            ├─ src/sources/openmeteo.py   forecast, soil moisture, ERA5 normals → anomalies
            ├─ src/sources/glam.py        corn-masked NDVI + baseline/anomaly
            ├─ src/compute/stats.py       trend, detrend, correlation (stdlib statistics)
            └─ src/build.py               inline ECharts + GeoJSON + data → index.html
```
Bundled, immutable assets (no runtime download): `assets/echarts.min.js`,
`src/geo/us_states.geo.json`, `src/geo/county_centroids.csv`.

## SharePoint (later)
The current `index.html` is perfect for `file://` and zipping. For SharePoint,
note that inline `<script>` is being blocked by tenant CSP (rolling out 2026), so
hosting the interactive HTML directly will need a CSP-compliant SPFx web part, or
an exported PDF/Office view. The pipeline already keeps data
(`data/dashboard_data.json`) separate from presentation to make that migration easy.

## Attribution
USDA NASS Quick Stats · Weather & soil moisture by Open-Meteo (CC-BY 4.0, ERA5) ·
NDVI by NASA Harvest GLAM (geoBoundaries: Runfola et al. 2020). Internal analytics use.
