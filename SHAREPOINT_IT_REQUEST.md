# Request: host & embed an interactive HTML dashboard in a SharePoint page

*(Fill in the [bracketed] bits and send this to your SharePoint / IT admin. It's written so they can act without back-and-forth.)*

---

**To:** [SharePoint / IT admin]
**From:** [your name]
**Re:** Displaying an interactive reporting dashboard on a SharePoint page

Hi [name],

I have an internal **corn-statistics dashboard** that's a single, self-contained HTML file (interactive charts + a clickable US map). I'd like to display it inside a SharePoint page for the team.

It **can't be uploaded to SharePoint directly** — SharePoint downloads `.html` files instead of showing them, and its Content Security Policy blocks the in-page scripts the dashboard uses. The standard supported way around this is to **host the file somewhere and embed it via the SharePoint Embed web part (an iframe)**. For that I need two small things from you.

## 1. A place to host one static file (HTTPS)

- **One file:** `index.html` (~2.6 MB). No server-side code, no database, no installer.
- Served over **HTTPS** from a location our machines' browsers can reach — an **internal IIS / intranet web server is ideal**; any static-file web host works.
- The host must **allow framing by SharePoint** — i.e. it must **not** send `X-Frame-Options: DENY`, and any `Content-Security-Policy: frame-ancestors` it sets must include our SharePoint domain (`*.sharepoint.com`). (`SAMEORIGIN`/`DENY` would block the embed.)

## 2. One SharePoint setting (site-level, no tenant admin needed)

- Add the host's domain to the target site's allowed-embed list:
  **Site Settings → HTML Field Security → "allow embedding from these domains."**
  A **site-collection admin / site owner** can do this — it does **not** require a global/tenant admin.

Once those two are in place, I'll add an **Embed** web part to the page and paste the file's URL. Done.

## Security notes (to make review quick)

- The dashboard runs **entirely client-side** in the viewer's browser and makes **no network calls** once loaded — all libraries and data are baked into the single file, so **no data leaves the network** at view time.
- It's a **static file**: nothing executes on the server.
- It needs **no "custom scripts" enabled** on SharePoint, no `.aspx`, and no tenant-admin changes — only the two items above.

## My questions

1. Is there an **internal HTTPS location** where I can publish a single static HTML file, reachable from our machines' browsers?
2. Can content from that location be **embedded (framed) inside a SharePoint page** (i.e. it doesn't block framing from `*.sharepoint.com`)?
3. Who can **add that domain to the embed allow-list** for our site, and can we get it added for: **[your SharePoint site URL]**?

**If hosting/embedding isn't possible:** would it instead be acceptable to share the dashboard as a **file link** (Teams / OneDrive / network share) that opens in the browser? The team could still use the full interactive dashboard that way — just not embedded in a SharePoint page.

Thanks!
[your name]
