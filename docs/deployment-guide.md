# Deployment Guide — Smart CRM, flow L4 (Technician assignment & appointments), track SE, tag v1.0

Author: Nguyen Thai Duc (2374802010117). Two commands build and start the whole system from an empty folder.

## 1. Requirements
- Docker Engine 24+ with Docker Compose v2 (Docker Desktop 4.x on Windows/macOS). Check: `docker compose version` → `v2.x`.
- Git 2.30+, about 2 GB free disk, internet access for the first build (pulls `python:3.12-slim`, `postgres:16-alpine`, `nginx:1.27-alpine`).
- Free host ports **3000** (API) and **5500** (web UI). The database port is NOT published. No Python or PostgreSQL needs to be installed.

## 2. Setup steps
1. Start in an EMPTY folder, then `git clone --branch v1.0 https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment.git smartcrm-l4`
2. `cd smartcrm-l4`
3. `cp .env.example .env`   (Windows cmd: `copy .env.example .env`)
4. `docker compose up -d --build`   (first build takes about 2–3 minutes)

Nothing else is needed: tables and sample data are created automatically on the first start (empty volume).
Stop: `docker compose down` · reset everything incl. data: `docker compose down -v`.

## 3. Environment variables (file `.env`, template `.env.example`)
| Name | Meaning | Sample value | Required |
|---|---|---|---|
| DB_HOST | Database host. Set to `db` automatically by docker compose; `localhost` when running without Docker | localhost | yes |
| DB_PORT | Database port | 5432 | yes |
| DB_NAME | Database name | smartcrm | yes |
| DB_USER | Database user (compose creates it) | smartcrm | yes |
| DB_PASSWORD | Database password — change it for a real deployment | doi-mat-khau-nay | yes |
| APP_PORT | Host port of the API (the UI calls `http://localhost:3000`) | 3000 | no |
| WEB_PORT | Host port of the web UI | 5500 | no |
| FRONTEND_ORIGIN | Origins allowed to call the API (CORS), comma-separated | http://localhost:5500,http://127.0.0.1:5500 | no |
| TEST_DB_NAME | Separate database used by the integration tests | smartcrm_test | no |

The app stops at start-up with `Thiếu biến môi trường: <NAME>` if a required variable is missing (values are never printed).

## 4. Sample data
Loaded automatically on the first start from `db/migrations/001_tao_bang_theo_ddl_bt1.sql` (6 tables) and `db/seed/001_du_lieu_mau.sql`:
**6** issue categories · **6** technicians (5 active) · **10** skill rows · **13** tickets — **3 NEW (MOI) tickets in centre 2**
(`BH000231/2026`, `BH000228/2026`, `BH000240/2026`), 1 NEW ticket in centre 1, 9 open tickets · 0 appointments.
Demo login (simulated, no password — real login is out of scope): employee id **3**, centre **2**, role *Quản lý trung tâm*.

Optional — official Smart CRM dataset (7,800 tickets, 38 technicians, 6 centres, 5 NEW tickets per centre):
`docker compose exec app python -m src.backend.seed_dataset --data data/official --reopen 5`

## 5. Verify it works
| Command / action | Expected result |
|---|---|
| `docker compose ps` | `db`, `app`, `web` all `Up … (healthy)` |
| `curl http://localhost:3000/health` (PowerShell: `curl.exe`) | `{"status":"ok","db":"up"}` |
| `curl -H "X-Employee-Id: 3" -H "X-Role: QUAN_LY" -H "X-Center-Id: 2" "http://localhost:3000/api/tickets?status=MOI"` | JSON with `"total":3` |
| `docker compose exec app python -m pytest -q` | `61 passed` |
| `docker compose exec app python -m scripts.run_tc TC-09` | eight-column test case ending with `PASS` |
| `docker compose exec app python -m scripts.run_tc TC-12` (run migration + sample data a **second time**) | `PASS`; row counts of the 6 tables are identical both times `[6, 6, 10, 13, 0, 0]` – nothing is duplicated |
| `docker compose down` then `docker compose up -d` again | `/health` is `ok` again and the data is exactly as before the restart – nothing duplicated (initialisation scripts run only on an empty volume) |
| Open `http://localhost:5500` → **Đăng nhập** (3 / 2) | list of 3 tickets → *Phân công* → *Đặt lịch hẹn* saves an appointment |

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| `port is already allocated` | Another program uses 3000/5500: stop it, or change `APP_PORT`/`WEB_PORT` in `.env` (if `APP_PORT` changes, also edit `src/frontend/api/config.js`). |
| `relation "ticket" does not exist` or empty list | An old volume skipped initialisation: `docker compose down -v` then `docker compose up -d --build`. |
| `app` exits immediately | `.env` is missing — repeat step 3. Read logs: `docker compose logs app --tail 50`. |
| `app` stays `starting` | The database is still initialising; wait 30 s and run `docker compose ps` again. |

## 7. Monitoring & alerts (optional)
Monitoring: `GET /health` checks app + database (used by the compose healthcheck); access logs show method, path and status of every request.
- **ALERT-01 API errors** — Measure: share of 5xx on `/api/*`, 5-minute window · Threshold: > 2 % in 2 consecutive windows · Notify: on-duty operator (chat) · Action: 1) `docker compose logs app --tail 200`; 2) if `/health` returns `"db":"down"`: `docker compose restart db`, then `/health` must return `"db":"up"`; 3) still failing after 10 min → escalate to the developer.
- **ALERT-02 Tickets close to their committed deadline (business)** — Measure: open tickets with `due_date` within 4 h, checked hourly · Threshold: > 10 per centre · Notify: service-centre manager (e-mail) · Action: open screen M1, filter NEW tickets, assign the overdue ones to technicians with the fewest open tickets (screen M2 suggestions).
