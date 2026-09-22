# New Gaia — the web re-platform (ROADMAP)

> ⚠ **Roadmap, not shipped.** Present as direction and as a de-risking story, never as available.
> Architecture-level detail here is client-safe; specifics marked internal are not.
> Last synced: 2026-09-22.

## The client-facing timeline (Andre's — use exactly this)
- **Ready now** — platform foundation built and tested, and the **web portal is live**.
- **January 2027** — first demo of the New Gaia.
- **June 2027** — alpha version.
- **Q4 2027** — start deploying.

## What it is
The migration of Gaia — today a .NET/WPF desktop application — to a modern
**.NET 10 API + React 19 single-page application**. The decisive point for any existing client:

> **The database does not change.** The same SQL Server database keeps running, with its triggers,
> stored procedures and history intact. Changes are **additive only** — nothing is dropped.

Consequences worth saying out loud to a client:
- **No data migration risk** — the data stays where it is.
- **The legacy rights model is reused, not replaced** — the same operator/group/rights tables.
- **Desktop and web coexist during migration** — both read and write the same data under the same
  rules, so a firm moves screen by screen, at its own pace.

## Architecture (client-safe framing)
- **Modular, layered architecture** (never say "monolith"): one deployable API partitioned into
  independent feature areas — orders, clients, products, transactions, reference data, navigation,
  configuration, positions, reports, user preferences — plus authorization and a dashboard BFF.
  Each area can later be extracted to its own service without re-architecting.
- **A request pipeline** every command and query flows through: metrics, request context, rate
  limiting, feature flags, logging, validation, **authorization / environment rights / field
  masking**, caching, audit, idempotency, retry, transaction, concurrency, business rules.
  Cross-cutting concerns are applied automatically, not re-implemented per feature.
- **Multi-environment tenancy** — portfolio management and fund management run as parallel
  environments, with the operator's rights enforced per environment.
- **Every action carries the real user** through to the database, so the existing audit trail keeps
  working unchanged.

## Security posture (lead with this framing)
- **BFF pattern — tokens never reach the browser.** The browser holds only an opaque, HttpOnly
  cookie; there is no token for a script to steal.
- **Two-factor / modern identity** via a standard identity provider (OIDC + PKCE), with a
  **kill switch**: disabling a user ends their live sessions within minutes, fail-closed.
- **HTTPS end-to-end**, security headers and a strict content-security policy on every response.
- **Deny-by-default authorization**, decided in the database on the firm's own rights model;
  **field-level security** (hide / mask / view / edit per user); navigation is server-driven and
  permission-filtered.
- **Audit everywhere**: every request, every authorization denial, every permission change, with
  PII and secrets redacted, plus scheduled retention and purge.
- Production hardening (secrets management, database least-privilege, TLS end-to-end, per-environment
  CORS) is an explicit **pre-production workstream** — present it as planned rigour, positively.
  ⚠ **Never present raw audit findings or specific gaps to a client.**

## Stack (versions are fine to name; counts are not)
ASP.NET Core 10 · React 19 + TypeScript + Vite · Keycloak 26 (OIDC/PKCE, BFF) · EF Core 10 + Dapper ·
Redis 7 (cache, sessions) · RabbitMQ 3 + MassTransit (async reports) · SignalR (real-time
notifications) · **SQL Server 2025** (client-facing target) · Serilog + OpenTelemetry · nginx.

## AI (roadmap only — the approved four)
**AI integration · AI over the database · a web/API library · AI-assisted UX.**
Gated by the same authorization and audit engine as everything else.
⚠ **Never invent specific AI features, models, capabilities or dates beyond these four.**

## Deck conventions for New Gaia content
No counts or metrics — name things, don't number them. Tech versions OK. Never "monolith".
SQL Server **2025**. AI stays roadmap-level. Security leads with **BFF · two-factor · HTTPS**.
