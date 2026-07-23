#!/usr/bin/env python3
# firewall_soilmoisture_test.py
# ---------------------------------------------------------------------------
# Standalone, PURE-STDLIB firewall reachability test for NASA/USDA soil-moisture
# sources (Crop-CASMA / SMAP), with your already-allowed GLAM NDVI hosts as a
# baseline so the result is unambiguous.
#
# HOW TO USE (on the WORK PC, where the firewall lives):
#   1. Copy this one file over (USB / email-to-self / paste into Notepad).
#   2. Run:   python firewall_soilmoisture_test.py
#   No installs needed. Python's stdlib only.
#
#   If your office uses a proxy, urllib picks it up from the environment, but you
#   can set it explicitly first (cmd examples):
#       set HTTPS_PROXY=http://yourproxy:8080
#   If the proxy does TLS interception (cert errors), point at the corporate CA:
#       set SSL_CERT_FILE=C:\path\to\corporate-ca.pem
# ---------------------------------------------------------------------------
import os, sys, ssl, socket, time, urllib.request, urllib.error

TIMEOUT = 12
UA = "Mozilla/5.0 (firewall-reachability-test; python-urllib)"

# (label, url) — GLAM = your existing allowed NDVI hosts; the rest are what we want to reach.
TARGETS = [
    ("GLAM  NDVI (already allowed)",      "https://api.glamdata.org/"),
    ("GLAM  NDVI (already allowed)",      "https://glam1.gsfc.nasa.gov/"),
    ("Crop-CASMA soil moisture (WANT)",   "https://nassgeo.csiss.gmu.edu/CropCASMA/"),
    ("Crop-CASMA / GMU-CSISS host",       "https://cloud.csiss.gmu.edu/"),
    ("SPoRT-LIS viewer (alt option)",     "https://weather.ndc.nasa.gov/sport/"),
]

def _opener(ctx):
    # build_opener keeps the default ProxyHandler (reads HTTP(S)_PROXY env) and just
    # swaps in our SSL context for HTTPS.
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

def check(url):
    """Return (verdict, detail). verdict in {ALLOWED, ALLOWED_CA, BLOCKED, DNS, ERROR}."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    # 1) normal, certificate-verifying attempt
    try:
        t0 = time.time()
        r = _opener(ssl.create_default_context()).open(req, timeout=TIMEOUT)
        code = getattr(r, "status", None) or r.getcode()
        return ("ALLOWED", "HTTP %s in %.1fs" % (code, time.time() - t0))
    except urllib.error.HTTPError as e:
        # The server (or proxy) sent an HTTP status back => the host is reachable.
        extra = " (may be a proxy block/auth page - glance at the browser)" if e.code in (403, 407) else ""
        return ("ALLOWED", "HTTP %s%s" % (e.code, extra))
    except urllib.error.URLError as e:
        reason = e.reason
        s = str(reason)
        # TLS-intercepting proxy: cert won't verify. Retry WITHOUT verification just to
        # learn whether the connection itself is permitted (if yes, it's allowed - you
        # only need the corporate CA installed, same as any HTTPS site).
        if isinstance(reason, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in s:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                r = _opener(ctx).open(req, timeout=TIMEOUT)
                code = getattr(r, "status", None) or r.getcode()
                return ("ALLOWED_CA", "HTTP %s but cert not trusted -> TLS-intercepting proxy; add corp CA (SSL_CERT_FILE)" % code)
            except Exception as e2:
                return ("BLOCKED", "TLS error, unverified retry also failed: %s" % e2)
        if isinstance(reason, socket.timeout) or "timed out" in s:
            return ("BLOCKED", "connection timed out (firewall is likely dropping it)")
        if ("getaddrinfo" in s or "Name or service not known" in s or "11001" in s
                or "nodename nor servname" in s or "Temporary failure in name resolution" in s):
            return ("DNS", "DNS lookup failed (blocked at DNS, or no internet on this box)")
        if "refused" in s or "reset" in s:
            return ("BLOCKED", "connection refused/reset")
        return ("ERROR", s)
    except socket.timeout:
        return ("BLOCKED", "connection timed out")
    except Exception as e:
        return ("ERROR", repr(e))

def main():
    line = "=" * 78
    print(line)
    print(" FIREWALL REACHABILITY TEST  -  NASA/USDA soil moisture vs GLAM baseline")
    print(line)
    print(" python     :", sys.version.split()[0])
    print(" HTTPS_PROXY:", os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "(none detected)")
    print(" CA bundle  :", os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or "(system default)")
    print("-" * 78)
    tag = {"ALLOWED": "ALLOWED   ", "ALLOWED_CA": "ALLOWED*CA", "BLOCKED": "BLOCKED   ", "DNS": "DNS-FAIL  ", "ERROR": "ERROR     "}
    results = []
    for label, url in TARGETS:
        v, d = check(url)
        results.append((label, v))
        print(" [%s] %s" % (tag[v], label))
        print("              %s" % url)
        print("              -> %s" % d)
    print("-" * 78)

    ok = lambda v: v in ("ALLOWED", "ALLOWED_CA")
    glam_ok  = any(ok(v) for l, v in results if l.startswith("GLAM"))
    casma_ok = any(ok(v) for l, v in results if l.startswith("Crop-CASMA"))
    print(" VERDICT:")
    if casma_ok:
        print("   -> Crop-CASMA is REACHABLE through this firewall. No new IT request needed.")
        print("      (If it read ALLOWED*CA, it works but needs the corporate CA bundle -")
        print("       same as any HTTPS site behind the proxy.)")
    elif glam_ok and not casma_ok:
        print("   -> GLAM works but Crop-CASMA is BLOCKED.")
        print("      Ask IT to allowlist:  nassgeo.csiss.gmu.edu   (and cloud.csiss.gmu.edu)")
        print("      Same kind of public HTTPS/443 gov-research host they already approved for GLAM.")
    else:
        print("   -> Even GLAM is unreachable here. You're probably NOT on the work network,")
        print("      or a proxy/CA needs setting. Run this ON the work PC; set HTTPS_PROXY /")
        print("      SSL_CERT_FILE if your office uses them, then re-run.")
    print(line)

if __name__ == "__main__":
    main()
