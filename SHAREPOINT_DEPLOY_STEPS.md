# Putting the corn dashboard on SharePoint — exact step-by-step

There are three ways to get it onto SharePoint. Pick by what you want:

| Route | Result | Keeps the interactive map/dropdown? | Needs a web host? |
|---|---|:---:|:---:|
| **A. Host + Embed (recommended)** | The **exact** dashboard, live inside a SharePoint page | ✅ Yes | ✅ Yes (an HTTPS host) |
| **B. Upload to a document library** | A file users click → **downloads** → open it | ✅ Yes (once opened) | ❌ No |
| **C. PDF export** | A static picture-of-the-dashboard shown in the page | ❌ No | ❌ No |

**If you want it identical to what you have now → Route A.** B and C are fallbacks if you can't get a host. Everything below is detailed for SharePoint Online (modern), 2026.

---

## ROUTE A — Host the file + Embed web part (keeps it 100% identical)

### A0. Confirm you have an HTTPS host (the one prerequisite)
The dashboard must be served from a web address your machine's browser can open. Best option in a corporate/firewalled setting: an **internal IIS / intranet web server** (keeps everything inside the network). Ask IT the question in `SHAREPOINT_IT_REQUEST.md`. You need a URL like `https://intranet.company.com/corn/index.html`.
- ✅ Good hosts: internal IIS site, internal static-file web server, or (if the org allows cloud) Azure Static Web Apps / Azure Blob static website.
- ❌ Not usable as the host: a SharePoint document library itself (SharePoint blocks framing its own files), or the 4 firewall domains (those are data APIs, not file hosts).

### A1. Publish `index.html` to the host
1. Run `run.bat` once on the internet machine so `index.html` is current.
2. Copy **just `index.html`** to the host's web folder. On IIS that's typically `C:\inetpub\wwwroot\corn\` → so the file lands at `C:\inetpub\wwwroot\corn\index.html`.
   - It's fully self-contained (charts + data are inside the one file), so **you only copy this one file** — nothing else.
3. Confirm the URL works: on the **work machine**, open `https://intranet.company.com/corn/index.html` in the browser. The full dashboard should load and be clickable. If it loads here, it will work embedded.

### A2. Make the host allow SharePoint to frame it (IIS admin, one-time)
By default a page can be framed unless a header forbids it. If clicking the embed later shows a blank box / "refused to connect," the host is sending a blocking header. The fix (hand this to whoever runs the host):
- On **IIS**, add this to the site's `web.config` (or set the headers in IIS Manager → HTTP Response Headers):
  ```xml
  <configuration>
    <system.webServer>
      <httpProtocol>
        <customHeaders>
          <remove name="X-Frame-Options" />
          <add name="Content-Security-Policy" value="frame-ancestors 'self' https://*.sharepoint.com" />
        </customHeaders>
      </httpProtocol>
    </system.webServer>
  </configuration>
  ```
  (Removes any `X-Frame-Options: DENY/SAMEORIGIN` and explicitly allows framing from SharePoint. `X-Frame-Options: ALLOW-FROM` is deprecated in modern browsers — the `frame-ancestors` CSP line is the correct way.)

### A3. Add the host's domain to SharePoint's allowed-embed list (site owner, one-time)
SharePoint only iframes domains on an allow-list. A **site owner / site-collection admin** (not a tenant admin) does this:
1. Go to the SharePoint **site** where the page will live.
2. Top-right **gear ⚙ → "Site information" → "View all site settings."**
3. Under **"Site Collection Administration"** click **"HTML Field Security."**
   - *(If you don't see "HTML Field Security," you're not a site-collection admin on this site — ask the site owner to do steps 3–5, or to grant you the role.)*
4. Choose **"Permit contributors to insert iframes from the following domains"** and add your host domain, e.g. `intranet.company.com` (domain only, no `https://`, no path).
5. Click **OK**.

### A4. Add the Embed web part to a page
1. Go to (or create) the page: site **→ + New → Page → Blank → Create page**, or open an existing page and click **Edit** (top-right).
2. Hover where you want it and click the round **“+” (Add a new web part).**
3. In the search box type **Embed** and click the **Embed** web part.
4. In its box, paste the **website address** — your `https://intranet.company.com/corn/index.html` URL — and press **Enter**.
   - (You can instead paste an `<iframe src="…" width="100%" height="1400"></iframe>` code to control the size directly.)
5. A live preview of the dashboard appears in the page.
6. Click **Republish** (top-right).

### A5. Size it so nothing is cut off
The dashboard is tall. Give the frame room:
- Put the Embed web part in a **full-width section** (Edit page → section layout → the full-width option), and/or
- Use the **iframe-code** form in A4 with a tall height, e.g. `height="1600"`. Adjust the number until there's no inner scrollbar.

### A6. Verify it survives CSP
On the published page's URL, add **`?csp=enforce`** at the end and reload (Microsoft's pre-enforcement test switch). The embedded dashboard should stay fully interactive — clicking the map and the dropdown still works. If it does, you're done.

### A7. Updating the data later
Each time you refresh the data: run `run.bat`, then **copy the new `index.html` over the old one on the host.** The SharePoint page's embed URL never changes, so the page shows the new version automatically (users may need a hard refresh, Ctrl+F5).

---

## ROUTE B — Upload to a document library (no host; users download-and-open)
This is the literal "upload to SharePoint." It does **not** render on a page — clicking the file downloads it, and the user opens the download (which then works fully, exactly like today).
1. Go to the SharePoint site → a **document library** (e.g. "Documents") or **Site Assets**.
2. **Upload → Files →** pick `index.html` (and re-upload the new one whenever you refresh data).
3. Tell users: **click the file → it downloads → open it from the Downloads bar/folder.** It opens in the browser and is fully interactive.
4. (Optional, nicer) On a SharePoint page, add a **Text** or **Button/Link** web part that links to the file, with a one-line note: *"Click to download and open the corn dashboard."*

*Trade-off:* zero setup and no admin, but it's a download each time, not an in-page dashboard.

---

## ROUTE C — Static PDF in the page (no host, no interactivity)
If you just need a viewable snapshot on the page and can't host:
1. On any machine, open `index.html`, pick the state/view you want, **Ctrl+P → Save as PDF** (repeat per view if needed).
2. Upload the PDF(s) to a document library (Route B, steps 1–2).
3. On a page: **Edit → “+” → "File viewer" web part → pick the PDF.** It renders inline.

*Trade-off:* no map clicking, no dropdown, and it's frozen at export time — a report, not the dashboard.

---

## Troubleshooting (Route A)
| Symptom | Cause | Fix |
|---|---|---|
| Embed shows **"…can't embed this content… add the domain to the allowed list"** | Host domain not allow-listed | Do **A3** (site owner adds the domain) |
| Embed box is **blank / "refused to connect"** | Host sends `X-Frame-Options: DENY`/`SAMEORIGIN` | Do **A2** (remove it, add the `frame-ancestors` header) |
| Clicking the file just **downloads** it | You used Route B (library), not the Embed web part | Use **A4** — paste the **URL** into an Embed web part, don't upload the .html to the page |
| Dashboard shows but **map/dropdown are dead**, console shows CSP errors | You pasted the **HTML** into a web part instead of the **URL** | Host the file (A1) and embed its **URL** (A4); never paste the page's HTML/script |
| Works normally but **breaks with `?csp=enforce`** | Something is loading outside the frame | Confirm you embedded the URL (frame), not inline HTML — inside an iframe CSP doesn't apply |
| Page shows the **old data** after an update | Browser cache | Re-copy `index.html` to the host (A7), then Ctrl+F5 |

## The decision, in one line
- Have (or can get) an internal HTTPS host → **Route A** = the exact dashboard, live in SharePoint. This is the recommendation.
- No host possible → **Route B** (download link) keeps full interactivity but isn't in-page; **Route C** (PDF) is in-page but static.
