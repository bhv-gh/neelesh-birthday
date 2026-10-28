# A little equity for Neelesh

A birthday gift from Harsha to **Neelesh Bhakth**, October 28, 2026.

A phone-first, dependency-free website with a Google / Meta share choice, an illustrated animated handoff, confetti, a downloadable SVG certificate, and sourced stock quotes.

**Live site:** https://bhv-gh.github.io/neelesh-birthday/

## Run locally

```sh
python3 -m http.server 8080
```

Open http://localhost:8080. Everything in the interface lives in `index.html`. Google Fonts are optional; the site works with its bundled system fallbacks. Stock quote snapshots are in `quotes.json`.

## Deployment

GitHub Actions refreshes quotes and publishes to GitHub Pages on pushes to `main`, manual runs, and every four hours. `scripts/fetch_quotes.py` uses Python's standard library, requests public Yahoo Finance quotes, and falls back to Google Finance. It preserves the last available snapshot when refreshing fails. Prices are indicative, with source and timestamp shown in the interface; no invented prices or historical charts are used.

The gift selection is saved only in the current browser using local storage. A downloaded certificate is a commemorative birthday promise, not a brokerage transaction or proof of stock ownership.

## The very small print

\* Redeemable after 75 years or when Google reaches $1,000, whichever comes later. The earliest date is October 28, 2101. This condition applies to either company selected.
