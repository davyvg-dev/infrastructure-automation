# @kk/marketing-site

Astro 5 + Tailwind 4 marketing site for Klantkraan, deployed to Cloudflare Pages.

## Scripts

| Command                                      | Purpose                                 |
| -------------------------------------------- | --------------------------------------- |
| `pnpm --filter @kk/marketing-site dev`       | Local dev server                        |
| `pnpm --filter @kk/marketing-site build`     | Production build (output in `dist/`)    |
| `pnpm --filter @kk/marketing-site preview`   | Preview the production build            |
| `pnpm --filter @kk/marketing-site typecheck` | `astro check` across all `.astro` files |

## Routes (current)

| Route                                      | Status                                                            |
| ------------------------------------------ | ----------------------------------------------------------------- |
| `/`                                        | Hero + value-prop, live                                           |
| `/loodgieters`                             | Stub, full copy in next iteration                                 |
| `/dakdekkers`                              | Stub                                                              |
| `/prijzen`, `/rekentool`, `/demo`, `/over` | Not yet scaffolded                                                |
| `/legal/*`                                 | Not yet scaffolded — content lives in `klantkraan/docs/04-legal/` |
| `/r/[slug]`                                | Per-client dashboard, future                                      |

Full route plan: `klantkraan/docs/08-tech/repo-architecture.md § apps/marketing-site`.

## Brand tokens

CSS-first via `src/styles/global.css` `@theme {}` block. Tokens follow the brand from
`klantkraan/docs/09-brand/visual-identity-brief.md` § 3-4.

| Token group      | Source of truth                |
| ---------------- | ------------------------------ |
| Colour           | `visual-identity-brief.md` § 3 |
| Typography       | `visual-identity-brief.md` § 4 |
| Layout / spacing | `visual-identity-brief.md` § 6 |

Fonts are self-hosted in `public/fonts/` (`src/styles/fonts.css`): Inter variable with the
weight and optical-size axes for headings and text, and Geist Mono for times, labels and figures.
Both OFL 1.1, from the Fontsource packages (see `public/fonts/OFL-NOTICE.txt`).

## Deployment

Cloudflare Pages, project `klantkraan-marketing`. See `klantkraan/docs/08-tech/infra-setup.md § Step 8`.
