"""Connectivity probe — what can this machine actually reach?

Run on a new/restricted machine:  python src/check_connectivity.py

It checks the dashboard's CURRENT sources, then probes candidate .gov
ALTERNATIVES. On a locked-down work network that only allowlists some domains,
the alternatives section tells us which blocked sources could be re-platformed
onto a domain the firewall already permits.

"reachable" = the server answered (even with an error code) => the firewall let
it through. "blocked" = the connection was refused/reset/timed out.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import http_util


def _probe(url):
    try:
        http_util.get_bytes(url)
        return True, "ok"
    except http_util.HttpError as exc:
        return True, f"HTTP {exc.status}"          # server replied => reachable
    except Exception as exc:                        # reset / refused / timeout
        msg = str(exc)
        return False, msg.split("] ")[-1][:70]


def main():
    cfg = config.load()
    http_util.configure(ca_bundle=cfg["ca_bundle"], delay=0.0,
                        timeout=cfg["request_timeout_seconds"], retries=1)
    key = (cfg.get("nass_api_key") or "").strip()
    if key.upper().startswith("PASTE_"):
        key = ""
    nass = "https://quickstats.nass.usda.gov/api/get_counts/?commodity_desc=CORN&state_alpha=IA"
    if key:
        nass += "&key=" + key

    current = [
        ("USDA NASS (crop data)", nass),
        ("Open-Meteo forecast (weather/soil)", "https://api.open-meteo.com/v1/forecast?latitude=41.6&longitude=-93.6&daily=temperature_2m_mean&forecast_days=1&timezone=auto"),
        ("Open-Meteo archive (normals/GDD)", "https://archive-api.open-meteo.com/v1/archive?latitude=41.6&longitude=-93.6&start_date=2020-06-01&end_date=2020-06-02&daily=temperature_2m_mean&timezone=auto"),
        ("GLAM new API (NDVI)", "https://api.glamdata.org/products/"),
    ]
    # OPTIONAL feature sources the dashboard USES beyond the core 4 — fetched at BUILD and
    # INLINED into index.html, so the RUNTIME never calls them. Reachability here only
    # affects whether THAT feature refreshes on THIS machine; nothing else breaks if blocked.
    optional = [
        ("NOAA CPC 8-14 day outlook (pop-up)", "https://www.cpc.ncep.noaa.gov/products/predictions/814day/814temp.new.gif"),
    ]
    # candidate .gov / alternative sources we could re-platform onto
    candidates = [
        ("NASA GLAM old (NDVI alt)", "https://glam1.gsfc.nasa.gov/api/doc/gettbl", "NDVI"),
        ("NWS api.weather.gov (weather alt)", "https://api.weather.gov/points/41.6,-93.6", "weather"),
        ("NOAA NCEI (climate-normals alt)", "https://www.ncei.noaa.gov/", "normals/anomaly"),
        ("NASA Earthdata CMR (satellite alt)", "https://cmr.earthdata.nasa.gov/search/collections.json?page_size=1", "NDVI"),
    ]

    print("=== CURRENT data sources (the 4 the dashboard REQUIRES) ===")
    for name, url in current:
        ok, info = _probe(url)
        print(f"  [{'REACHABLE' if ok else '  BLOCKED'}]  {name:<38} ({info})")

    print("\n=== OPTIONAL feature sources (fetched at BUILD, inlined; not required) ===")
    cpc_blocked = False
    for name, url in optional:
        ok, info = _probe(url)
        print(f"  [{'REACHABLE' if ok else '  BLOCKED'}]  {name:<42} ({info})")
        if not ok:
            cpc_blocked = True

    print("\n=== CANDIDATE .gov alternatives (for blocked sources) ===")
    reachable_alts = []
    for name, url, powers in candidates:
        ok, info = _probe(url)
        print(f"  [{'REACHABLE' if ok else '  BLOCKED'}]  {name:<38} ({info})")
        if ok:
            reachable_alts.append((name, powers))

    print("\n--- Summary ---")
    if reachable_alts:
        print("These reachable alternatives could replace blocked sources:")
        for name, powers in reachable_alts:
            print(f"   - {name}  ->  could provide: {powers}")
        print("Send this output to whoever is helping you and we can re-platform.")
    else:
        print("No alternative .gov sources are reachable either.")
        print("Either ask IT to allowlist the blocked domains, or refresh the data")
        print("on a machine with internet and copy the data/ folder + index.html over.")
    if cpc_blocked:
        print("\nNOTE: NOAA CPC is BLOCKED on this machine, so the 8-14 day outlook pop-up")
        print("won't refresh here (everything else still works). To keep it current: build")
        print("index.html on a machine that can reach cpc.ncep.noaa.gov, or ask IT to")
        print("allowlist cpc.ncep.noaa.gov. The runtime never calls it — it's inlined.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
