# Nifty valuation gauges — "Valuation till 2026 end"

A single-page dashboard showing where four NSE indices (Nifty 50, Midcap 100,
Smallcap 250, Nifty 500) sit today versus their own trend growth since the 2024 peak.

Each dial compares the current level against a **trend value**:

```
trend value = 2024 ATH × (1 + CAGR)²
```

- **Deep green** — at or below the 2024 all-time high
- **Green** — above the ATH but below the trend value
- **Red** — above the trend value (grown faster than its own historical rate)

CAGR is the only adjustable input on the page. The full method is written into the
collapsible panel at the top of the page.

> Illustrative model, not investment advice. The trend value is anchored to a cyclical
> peak, so it sets an aggressive bar by design.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The whole dashboard — self-contained, no build step, no dependencies |
| `data.json` | Current index values the page reads at load (seed values included) |
| `fetch.py` | Nightly fetcher that rewrites `data.json` |
| `requirements.txt` | Python deps for `fetch.py` (`yfinance`) |
| `.github/workflows/update.yml` | Scheduled GitHub Action that runs `fetch.py` nightly |

`index.html` has the current values hardcoded as a fallback, so it renders even if
`data.json` is missing. When `data.json` is present, its `cur`/`date` values win and a
"Data last updated" line appears under the gauges.

## Preview locally

Because the page fetches `data.json`, open it through a tiny local server (opening the
file directly with `file://` will skip the fetch and just use the fallback values):

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Push to GitHub

Create an **empty** repo on GitHub first (no README/licence), then from this folder:

```bash
git init
git add .
git commit -m "Nifty valuation gauges dashboard"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

Replace `<username>` and `<repo>`. If you use SSH, swap the remote for
`git@github.com:<username>/<repo>.git`.

## Publish with GitHub Pages

1. Repo → **Settings** → **Pages**.
2. **Source**: *Deploy from a branch*. **Branch**: `main`, folder `/ (root)`. Save.
3. Wait ~1 minute; your site is live at `https://<username>.github.io/<repo>/`.

## How the nightly update works

`.github/workflows/update.yml` runs on a schedule (13:00 UTC = 18:30 IST, weekdays,
after NSE close). Each run:

1. installs `yfinance`,
2. runs `fetch.py`, which pulls the latest close for each index and rewrites `data.json`
   (keeping the previous value for any symbol that fails, so a hiccup never blanks a gauge),
3. commits `data.json` — which triggers Pages to redeploy with fresh numbers.

You can also trigger it by hand: repo → **Actions** → *Update index data* → **Run workflow**.

### One-time permission check

The commit step needs write access. Repo → **Settings** → **Actions** → **General** →
**Workflow permissions** → select **Read and write permissions** → Save.

### Verify the tickers

`fetch.py` uses Yahoo Finance symbols. Confident: `^NSEI` (Nifty 50) and
`NIFTYSMLCAP250.NS` (Smallcap 250). **Double-check** `NIFTY_MIDCAP_100.NS` (Midcap 100)
and `^CRSLDX` (Nifty 500) — Yahoo's Indian index symbols are inconsistent. Run
`python fetch.py` locally once and confirm all four print an `OK` line with a sane number;
if one is empty, try the alternate ticker noted beside it in `fetch.py`.

Yahoo is an unofficial endpoint — fine for a personal board, but for anything you rely on,
switch `fetch.py` to a broker API you already have (Zerodha Kite, Upstox, Angel One) and
store the key as a GitHub Actions **secret** (`Settings → Secrets and variables → Actions`).

## Adjusting the model

The 2024 ATHs and CAGRs live in the `DATA` array near the top of the `<script>` block in
`index.html`. The Smallcap 250 and Nifty 500 ATH anchors are approximate — replace them
with exact NSE factsheet closes when you have them.
