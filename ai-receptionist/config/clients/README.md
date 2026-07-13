# Client configs (multi-tenant routing)

One server process hosts many clients. Drop a real client's config here as
`config/clients/<slug>.yaml` and it becomes reachable at its own origin — the server routes
each request to the right config by the **first label of the Host header**:

    https://<slug>.klantkraan.nl   ->   config/clients/<slug>.yaml

`<slug>` must match `[a-z0-9-]` (a DNS label). Example: `config/clients/van-dijk.yaml` is served
at `https://van-dijk.klantkraan.nl`.

- A file dropped here is **immediately routable** — treat this directory as production.
- An unknown host (the sslip.io demo, `localhost`, the apex domain) falls back to the single
  config named by `BUSINESS_CONFIG` — so the live demo and single-tenant runs are unchanged.
- Config is cached per file at load; **restart the server** after editing a client's YAML.
- Testing without DNS: add `?client=<slug>` or an `X-Client-Slug: <slug>` header to a request.

Each client's config is the exact same shape as `config/klantkraan-demo.yaml` (generate one with
`python -m app.scaffold "<Bedrijf>"`, then move it here as `<slug>.yaml`). Per-tenant state — the
session store and the `sim` provider's `data/bookings-<slug>.json` — is namespaced by slug, so
clients never share slots or conversations.

Prospect sales demos live in `config/prospects/` and are **not** routed (run them single-tenant
via `BUSINESS_CONFIG=config/prospects/<name>.yaml`); only files here are multi-tenant.

*(This README keeps the directory in git and is never routed — routing only matches `*.yaml`.)*
