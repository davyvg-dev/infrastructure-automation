# @kk/domain

Shared TypeScript types for the Klantkraan business domain: `Client`, `Call`, `Booking`, `Review`, `Suppression`, `SubscriptionSnapshot`, and supporting unions.

Imported by `@kk/marketing-site`, `@kk/api`, future `@kk/db`, future `@kk/attio`, future `@kk/billing`. Single source of truth for naming so a `Call` is the same shape everywhere.

No runtime code. No external deps. Bump major when a field name or required field changes.
