# Run InvoiceFlow on a NAS

Put InvoiceFlow on your home/office NAS so every phone, tablet, and computer on the **same Wi‑Fi / LAN** can open the same invoices.

There is **no login**. Keep it on your private network. Do **not** port-forward 8765, and do not put it on QuickConnect / a public URL.

Use **one device at a time**. The last save wins — there is no merge.

---

## Which method?

| Your NAS | Use |
|----------|-----|
| Synology DSM 7, QNAP, Unraid, TrueNAS SCALE, or any machine with Docker | **A. Docker** (recommended) |
| Linux NAS with Python 3, no Docker | **B. Python on the NAS** |
| You only want the files stored on the NAS, and still run the app on a PC/Mac | **C. Shared folder** (Dropbox-style) |

---

## A. Docker (recommended)

Works with Synology **Container Manager**, QNAP **Container Station**, Unraid, TrueNAS SCALE Apps, and `docker compose` on Linux.

1. Copy the whole **InvoiceFlow** folder onto a NAS share, for example:
   - Synology: `docker/invoiceflow` (File Station)
   - Generic: `/volume1/docker/invoiceflow` or `/share/invoiceflow`
2. On the NAS, start it from that folder:

```bash
cd /path/to/InvoiceFlow
docker compose up -d
```

**Synology Container Manager (no SSH):** Project → Create → path = the InvoiceFlow folder → it will pick up `docker-compose.yml` → Start.

3. On any device on the same network, open:

```text
http://YOUR-NAS-IP:8765
```

Example: `http://192.168.1.50:8765`

Find the NAS IP in your router, or:
- Synology: Control Panel → Info Center → Network
- QNAP: Control Panel → Network & File Services

4. Settings → Multi-Device Sync should show **Linked (NAS / LAN server)**.

Data is stored in `data/invoiceflow-data.json` next to the compose file. Back that file up with the rest of the NAS.

**Firewall:** allow TCP **8765** on the LAN if the NAS firewall is on.

**Port already in use?** In `docker-compose.yml` change `"8765:8765"` to `"9000:8765"` (left side is the port you open in the browser).

Stop:

```bash
docker compose down
```

---

## B. Python on the NAS (no Docker)

1. Copy the InvoiceFlow folder onto the NAS.
2. Enable SSH (or use Task Scheduler / a persistent terminal).
3. Run:

```bash
chmod +x "Run InvoiceFlow NAS.sh"
./Run\ InvoiceFlow\ NAS.sh
```

Or:

```bash
python3 server.py --lan
```

4. Open `http://YOUR-NAS-IP:8765` from other devices. Leave the process running.

To start at boot, add that command to DSM **Task Scheduler** (Triggered task → Boot-up) or a systemd unit.

---

## C. Shared folder only (run the app on a PC/Mac)

Same idea as Dropbox: the files live on the NAS, each computer still runs a local launcher.

1. Copy InvoiceFlow onto a NAS share.
2. Map that share on Windows (`Z:\InvoiceFlow`) or mount it on Mac/Linux.
3. Run **Run InvoiceFlow PC / Mac / Linux** from the mapped folder.
4. Browser still opens `http://127.0.0.1:8765` on **that** computer.

Phones cannot use this method (they need method A or B).

---

## Move existing invoices onto the NAS

**Easiest:** on the old computer, Settings → **Export JSON Backup**. After the NAS app is open, Settings → **Import JSON Backup**.

**If you already used Dropbox / the desktop launcher:** copy `invoiceflow-data.json` (often in `InvoiceFlow/app/` or next to `index.html`) into the NAS `data/` folder as `invoiceflow-data.json`, then start Docker/Python.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| Page won’t load from a phone | Confirm phone is on the same Wi‑Fi (not cellular / guest Wi‑Fi). Use the NAS LAN IP, not `127.0.0.1`. |
| Connection refused | Container/script is not running. On Synology, start the Container Manager project. |
| Works on NAS, not from PC | NAS firewall — allow TCP 8765 from the LAN. |
| “index.html missing” | The compose file must sit next to `index.html` and `server.py`. |
| Lost invoices after restart | Check that `data/invoiceflow-data.json` is on a real NAS folder, not a throwaway container filesystem. |
