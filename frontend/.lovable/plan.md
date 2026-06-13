
# EchoMind — Frontend Plan

A clean, focused frontend for your "decision memory" backend. Three flows: **Search**, **Manual Capture**, and **AI Upload → Review & Confirm**, plus a small health indicator.

## Pages / routes

```
/            Landing + Search (primary surface)
/capture     Manual Capture form
/upload      AI Upload → Review & Confirm (two steps in one route)
```

Shared top nav with logo, links to the three flows, and a tiny health dot (green/red) driven by `GET /api/health`.

## Flow details

**1. Search (`/`)**
- Big query input + "Search Memory" button.
- On submit → `POST /api/search`.
- Results show two clear blocks:
  - "AI Recommendation" card (the `recommendation` string).
  - "Historical Evidence" list — collapsible cards per `case` showing problem, context, decision, reasoning, outcome, date.
- Empty state before any search; loading skeletons during the call; error toast on failure.

**2. Manual Capture (`/capture`)**
- Form with required fields (problem, decision, reasoning) and optional fields (context, options considered, outcome).
- Client-side validation for required fields.
- Submit → `POST /api/capture` → success toast with `decision_id`, form resets.

**3. AI Upload (`/upload`)**
- Step 1: dropzone for `.txt` / `.pdf` → `POST /api/upload` (multipart, no Content-Type header).
- Step 2: pre-filled, editable review form of the extracted data → `POST /api/confirm` → success toast.
- "Start over" button to upload another doc.

## Design

Modern, slightly editorial feel — calm neutrals with one strong accent so the AI recommendation pops. Generous whitespace, real typography (not Inter), subtle motion on result reveals. Sidebar-free, top-nav layout suits a 3-screen demo.

If you'd like to choose the visual direction, I can render 2–3 design directions after you approve this plan. Otherwise I'll just build a cohesive one.

## Technical notes

- **API base URL:** read from `VITE_API_BASE_URL` (default `http://localhost:8000`) so you can repoint it without code changes. Documented in a short `.env.example`.
- **Local backend + hosted preview:** since the backend runs on `localhost:8000`, the hosted Lovable preview cannot reach it (browser blocks cross-origin to localhost, and your machine isn't reachable from the preview server). For the demo, run the frontend locally (`bun dev`) alongside your backend, or expose the backend via a tunnel (ngrok / cloudflared) and set `VITE_API_BASE_URL` to that URL. I'll add a small banner in dev when `/api/health` fails so it's obvious.
- **CORS:** your FastAPI backend must allow the frontend origin (`http://localhost:5173` for dev). Add `CORSMiddleware` on the backend side — I'll note this in the README.
- **Tiny API client** in `src/lib/api.ts` wrapping all 5 endpoints with typed request/response shapes and a single `callAPI` helper that throws on `!res.ok` using `detail`.
- **TanStack Query** for search/health (caching + loading states); plain mutations for capture/upload/confirm.
- No auth, no database, no Lovable Cloud — purely a frontend talking to your local API.

## Out of scope (ask if you want them)

- Login / user accounts
- Saving search history
- Listing all stored decisions (no endpoint for that yet)
- Deploying the backend
