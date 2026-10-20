# Prospect configs (real company PII)

Each `config/prospects/<name>.yaml` is a sales-demo config built from a **real** prospect —
company name, phone number, and address of a third party. That is PII, so this directory is
**gitignored and never committed**. It still rsyncs to the server on deploy, so live demos keep
working.

Generate one, don't hand-write it:

    python -m app.scaffold "<Bedrijf>"            # blank template to fill in
    python -m app.extract "<Bedrijf>" --url <site> # scrape -> cited draft

Prospect demos run single-tenant (`BUSINESS_CONFIG=config/prospects/<name>.yaml`) and are **not**
routed. A paying client's config moves to `config/clients/<slug>.yaml` instead.

*(This README keeps the directory in git; only `*.yaml` here is ignored.)*
