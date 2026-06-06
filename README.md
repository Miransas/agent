# CourierX Console

The dashboard for [CourierX](https://courierx.io). Private until launch.

This is the customer-facing console at `console.courierx.io` — where users will manage their API keys, verified domains, sent emails, and team settings.

## Status

🚧 **Pre-launch.** Foundation built, mock-data demo ready, real API integration pending.

## Stack

- **Framework:** Next.js 16 (App Router)
- **Styling:** Tailwind CSS v4 + shadcn/ui
- **Charts:** recharts
- **Smooth scroll:** Lenis
- **Fonts:** IBM Plex Sans + JetBrains Mono
- **Deployment:** Vercel (private deploy)

## Routes

```
(auth)/login          → mock login (no real auth yet)
(dashboard)/dashboard → overview with metrics + recent emails (mock data)
(dashboard)/emails    → email log (mock data, stub)
(dashboard)/domains   → sending domain verification (stub)
(dashboard)/api-keys  → API key management (stub)
(dashboard)/logs      → request logs (stub)
(dashboard)/settings  → workspace settings (stub)
```

## Local development

```bash
git clone git@github.com:Miransas/courierx-console.git
cd courierx-console
npm install
npm run dev
```

Open `http://localhost:3000` (redirects to `/dashboard`).

## Design tokens

Matches the [courierx-web](https://github.com/sardorazimov/courierx-web) landing site for visual continuity:

- Base: `#050505`
- Elevated (cards/sidebar): `#0a0a0a`
- Accent: `#8CFF2E` (neon green)
- Borders: `rgba(255,255,255,0.06)`
- Fonts: IBM Plex Sans (UI), JetBrains Mono (code/keys/ids)
- Radius: 8px default, 12px cards, pill buttons
- Dark mode only

## Roadmap

1. ✅ Foundation: route structure, layout, sidebar, topbar, primitives
2. ✅ Collapsible sidebar + Domains route
3. ✅ Overview demo mode (mock data, charts, recent emails list)
4. ⏳ Mock login + protected route guard
5. ⏳ Emails list/detail wired to real API
6. ⏳ API Keys CRUD
7. ⏳ Settings + team management
8. ⏳ Billing (when Managed launches)

## Other repos in the CourierX project

- [courierx-web](https://github.com/sardorazimov/courierx-web) — marketing site (public)
- [courierx-api](https://github.com/Miransas/courierx-api) — Rust HTTP API (public)
- [courierx-worker](https://github.com/Miransas/courierx-worker) — Rust queue consumer (public)

## License

Private. © Miransas.
