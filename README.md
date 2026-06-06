# CourierX Console

> ⚠️ **Private repository.** Source-available dashboard for [CourierX](https://github.com/miransas/courierx-api).

The web dashboard for managing CourierX workspaces — API keys, send logs, domain verification, and analytics.

Live at [console.courierx.io](https://console.courierx.io).

## Stack

- Next.js 16 (App Router)
- TypeScript + Tailwind v4 + shadcn/ui
- Connects to CourierX API (`api.courierx.io`)

## Quick start

```bash
git clone https://github.com/Miransas/courierx-console
cd courierx-console
npm install
cp .env.example .env.local
npm run dev
```

## Architecture

```
console.courierx.io  → this repo
       │
       ▼ (HTTPS, JWT auth)
api.courierx.io      → courierx-api (Rust)
       │
       ▼ (Postgres)
[email queue]        → courierx-worker (Rust)
       │
       ▼
[SES / Resend / SMTP]
```

## Related repos

| Repo | Visibility |
|------|------------|
| [courierx-web](https://github.com/sardorazimov/courierx-web) | Public |
| [courierx-api](https://github.com/miransas/courierx-api) | Public |
| [courierx-worker](https://github.com/miransas/courierx-worker) | Public |

## License

Proprietary. All rights reserved.

---

Part of [Miransas](https://miransas.com).