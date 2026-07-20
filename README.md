# InvoiceFlow

**Free, offline invoice creator & time tracker for small businesses.**

A single-file web app — no install, no account, no server. Just open it in your browser.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Offline](https://img.shields.io/badge/Works-Offline-brightgreen)
![No Backend](https://img.shields.io/badge/Backend-None-lightgrey)

## Features

### Invoicing
- Create professional invoices with line items, tax, discounts, partial payments
- Status tracking: Draft → Sent → Paid / Partial / Overdue (auto-detected)
- Client directory
- PDF export via browser Print → Save as PDF
- Business branding (name, address, Tax ID, currency, invoice prefix, terms)

### Time & Labor Tracker
- Quick-log labor hours, travel time, mileage, materials, and expenses
- Default rates for labor / travel / mileage (configurable)
- Unbilled entry list with multi-select
- **One-click “Create Invoice from Selected”** — turns time entries into invoice line items and marks them billed
- Unbilled entries on Dashboard with multi-select

### Privacy & Data
- 100% local — everything stored in browser `localStorage`
- One-click JSON export / import for backup or moving between devices
- No tracking, no accounts, no cloud

## Quick Start

### Recommended — Dropbox multi-device (Windows / Mac / Linux)

Keep the app in a synced folder (e.g. Dropbox) with this layout:

```text
InvoiceFlow/
  Run InvoiceFlow PC.bat
  Run InvoiceFlow Mac.command
  Run InvoiceFlow Linux.sh
  app/
    index.html
    server.py
    server.ps1
    invoiceflow-data.json   ← shared data (auto-created)
```

| OS | Start with | Needs |
|----|------------|--------|
| **Windows** | `Run InvoiceFlow PC.bat` | PowerShell (built-in) |
| **Mac** | `Run InvoiceFlow Mac.command` | Python 3 |
| **Linux** | `Run InvoiceFlow Linux.sh` | Python 3 + `chmod +x` once |

Then open **http://127.0.0.1:8765/index.html** (launchers open this for you).  
Settings → Multi-Device Sync should show **Linked (Dropbox app folder)**.

**Linux one-time:**
```bash
chmod +x "Run InvoiceFlow Linux.sh"
./Run\ InvoiceFlow\ Linux.sh
```

Use **one computer at a time**; wait for cloud sync before switching.

### Option — open `index.html` alone
Works for a quick look, but multi-device Dropbox sync needs the launcher/server above.

### Dev server
```bash
cd app   # or repo root if flat
python3 server.py
# http://127.0.0.1:8765/index.html
```

## Screenshots

*(Open the app and take your own — dark modern UI with dashboard, quick log, time log, invoices, clients, settings)*

## Default Rates (Settings)

| Setting            | Default   |
|--------------------|-----------|
| Labor rate         | $75 / hr  |
| Travel rate        | $50 / hr  |
| After hours rate   | $112.50 / hr |
| Mileage rate       | $0.70 / mi|
| Invoice prefix     | INV-      |
| Payment terms      | Net 30    |

Change these anytime under **Settings**.

## Workflow Example

1. **Settings** → set business info + rates  
2. **Dashboard** → Quick Log labor / travel as you work  
3. Select unbilled entries → **Create Invoice from Selected**  
4. Review / edit the invoice → Save  
5. Click **PDF** → Print → Save as PDF → send to client  
6. When paid, edit invoice → set Amount Paid + status Paid  

## Data Backup

- **Export JSON** (Invoices page or Settings) regularly  
- Import the JSON on another computer/browser to restore everything  

## Tech

- Pure HTML + CSS + Vanilla JS  
- No frameworks, no build step, no dependencies  
- Works completely offline  
- Responsive (desktop + mobile)

## License

MIT — free for personal and commercial use. See [LICENSE](LICENSE).

## Contributing

PRs welcome. Keep it simple and dependency-free.

---

Built for freelancers, contractors, consultants, and small shops who want something fast, private, and free.
