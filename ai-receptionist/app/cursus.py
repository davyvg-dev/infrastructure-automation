"""De e-mailcursus "Gemiste omzet": vier Nederlandse lessen, verstuurd via Resend.

The calculator on klantkraan.nl offers a free 4-part course by mail; this module owns the
subscriber ledger, the lesson copy, the schedule, and the sending. The opt-in endpoint
(server.py) and the daily timer both call into here.

This is opt-in nurture mail, which inverts every rule of the cold-outreach sequencer
(scripts/sequence.py): dynamic subscribers instead of a hardcoded list, Resend instead of
Gmail SMTP, and a List-Unsubscribe header plus a footer afmeldlink on every mail, which
Telecommunicatiewet art. 11.7 requires for mailings and cold 1:1 outreach deliberately
omits. The ledger *design* is inherited: schedule anchored on the opt-in timestamp,
explicit halt states (unsubscribed / bounced), and a corrupt store that exits loudly
rather than defaulting to empty and re-mailing everyone lesson 1.

Two sending rules:
- At most ONE lesson per subscriber per run, so a timer that slipped a week catches up
  over consecutive days instead of bursting three lessons into one inbox.
- Each send carries an Idempotency-Key (cursus-<email>-les-<n>); a crashed run that
  re-sends after recording nothing cannot double-deliver within Resend's 24h window.

Completion is the point: the moment lesson 4 is sent the subscriber is scored onto the
pipeline board as an inbound opt-in lead. `pipeline.qualify` has an explicit inbound
bypass, so a course completer skips the BV-only gate; the calculator consent is exactly
what legally opens the eenmanszaak/VOF market (research/PLAN 2026-08-12, Phase 2.1).

Store: data/cursus/subscribers.json. Everything under data/ survives deploys (deploy.sh
excludes it from the rsync --delete), same protection leads.jsonl relies on.

Config (.env):
  RESEND_API_KEY    unset = mailer prints instead of sends; `send` then exits 1 when
                    lessons were due, so the timer unit fails visibly (digest rule).
  CURSUS_BASE_URL   host for afmeldlinks, default https://demo.klantkraan.nl
  CURSUS_SECRET     HMAC key for afmeldlink tokens; unset = auto-generated once into
                    data/cursus/secret, so the server manages itself.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from . import mail_layout, mailer, pipeline, settings

LESSON_NUMBERS = (1, 2, 3, 4)

# Day offsets from opt-in. Lesson 1 goes out immediately (the opt-in endpoint triggers a
# send for the new subscriber; the daily timer is the catch-all), then the spacing widens
# the way a course should: quick while attention is warm, calmer toward the pitch.
LESSON_DAY = {1: 0, 2: 2, 3: 5, 4: 9}

DEFAULT_BASE_URL = "https://demo.klantkraan.nl"


# --- time ---------------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


# --- store --------------------------------------------------------------------------------


def cursus_dir() -> Path:
    # Read settings.DATA_DIR at call time, not import time, so the tests' data_dir
    # fixture isolates this store the same way it isolates the others.
    return settings.DATA_DIR / "cursus"


def store_path() -> Path:
    return cursus_dir() / "subscribers.json"


def load() -> dict:
    path = store_path()
    if not path.exists():
        return {"subscribers": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # A corrupt ledger must never read as empty: that would forget who already got
        # which lesson and re-mail the whole list from lesson 1.
        sys.exit(f"cursus: {path} is corrupt ({exc}); fix or restore it before sending")
    if not isinstance(data, dict) or not isinstance(data.get("subscribers"), dict):
        sys.exit(f"cursus: {path} has an unexpected shape; refusing to guess")
    return data


def save(data: dict) -> None:
    cursus_dir().mkdir(parents=True, exist_ok=True)
    path = store_path()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def normalize(email: str) -> str:
    return (email or "").strip().lower()


def add(
    email: str,
    *,
    name: str | None = None,
    source: str = "site",
    now: datetime | None = None,
) -> dict:
    """Subscribe an address; idempotent. A re-signup after an afmelding is a fresh consent,
    so it clears the halt flag, but lesson history is never reset: someone who finished the
    course and signs up again does not get it a second time."""
    email = normalize(email)
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError(f"not an e-mail address: {email!r}")
    now = now or _now()
    data = load()
    sub = data["subscribers"].get(email)
    if sub is None:
        sub = {
            "email": email,
            "name": (name or "").strip() or None,
            "source": source,
            "opted_in": _iso(now),
            "lessons": {},
        }
        data["subscribers"][email] = sub
    else:
        if name and not sub.get("name"):
            sub["name"] = name.strip()
        if sub.get("unsubscribed"):
            sub.pop("unsubscribed", None)
            sub["opted_in"] = _iso(now)  # new consent, new anchor for whatever is unsent
    save(data)
    return sub


def stop(email: str, *, bounced: bool = False, now: datetime | None = None) -> bool:
    """Halt sending. Returns True if the address was known. `bounced` is the delivery-side
    halt; the default is an afmelding (consent withdrawn)."""
    email = normalize(email)
    data = load()
    sub = data["subscribers"].get(email)
    if sub is None:
        return False
    sub["bounced" if bounced else "unsubscribed"] = _iso(now or _now())
    save(data)
    return True


# --- afmeldlink ---------------------------------------------------------------------------


def _secret() -> str:
    env = os.getenv("CURSUS_SECRET")
    if env:
        return env
    path = cursus_dir() / "secret"
    if not path.exists():
        cursus_dir().mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_hex(32), encoding="utf-8")
        path.chmod(0o600)
    return path.read_text(encoding="utf-8").strip()


def token(email: str) -> str:
    digest = hmac.new(_secret().encode(), normalize(email).encode(), hashlib.sha256)
    return digest.hexdigest()[:32]


def verify_token(email: str, tok: str) -> bool:
    return hmac.compare_digest(token(email), (tok or "").strip())


def unsubscribe_url(email: str) -> str:
    base = os.getenv("CURSUS_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    email = normalize(email)
    return f"{base}/cursus/uitschrijven?e={quote(email)}&t={token(email)}"


# --- lesson copy --------------------------------------------------------------------------
#
# Written in "u", like the site. Numbers stay consistent with the rekentool model (about a
# third of missed callers books elsewhere) and the market research (leadplatform fees run
# beyond €200 per won job). No founder name, no em-dashes, plain trade Dutch.


def _greeting(sub: dict) -> str:
    name = (sub.get("name") or "").strip()
    return f"Hoi {name.split()[0]}," if name else "Hoi,"


def _blocks_1(sub: dict) -> list[mail_layout.Block]:
    return [
        mail_layout.Para(_greeting(sub)),
        mail_layout.Para(
            "Welkom bij de cursus. Vier korte mails, verspreid over anderhalve week. "
            "Geen huiswerk, wel een paar sommen die u waarschijnlijk nog nooit voor uw "
            "eigen bedrijf heeft gemaakt."
        ),
        mail_layout.Heading("De oproep die u niet hoort"),
        mail_layout.Para(
            "U kunt niet opnemen terwijl u werkt. Op de ladder, onder een vloer, bij een "
            "klant aan tafel. Dat is geen slordigheid, dat is het vak. Maar aan de andere "
            "kant van die lijn staat iemand met een lekkage en een lijstje bedrijven."
        ),
        mail_layout.Para(
            "Uit onderzoek onder kleine bedrijven blijkt dat meer dan de helft van de "
            "telefoontjes onbeantwoord blijft, en dat de meeste bellers geen voicemail "
            "inspreken. Ze bellen gewoon de volgende op het lijstje."
        ),
        mail_layout.Heading("De rekensom"),
        mail_layout.Para(
            "Stel: drie gemiste oproepen per week, en ongeveer een op de drie daarvan was "
            "een echte klus. Dat is een klus per week die naar een ander gaat. Bij een "
            "gemiddelde klus van 450 euro praat u over ruim 20.000 euro per jaar."
        ),
        mail_layout.Para(
            "Uw eigen getallen invullen kan met de rekentool: klantkraan.nl/rekentool."
        ),
        mail_layout.Para(
            "In de volgende les: wat een lead u kost als u hem via een platform "
            "terugkoopt."
        ),
        mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"),
    ]


def _blocks_2(sub: dict) -> list[mail_layout.Block]:
    return [
        mail_layout.Para(_greeting(sub)),
        mail_layout.Para(
            "Vorige les ging over de klus die naar een ander gaat. Deze les gaat over "
            "wat het kost om diezelfde klus terug te kopen."
        ),
        mail_layout.Heading("De platformsom"),
        mail_layout.Para(
            "Op leadplatforms zoals Werkspot betaalt u per lead, en dezelfde lead gaat "
            "ook naar drie tot vijf concurrenten. U wint er misschien een op de vier of "
            "vijf. Reken dat door en een gewonnen klus kost al snel meer dan 200 euro "
            "aan leadkosten. Voor werk dat vroeger gewoon via uw eigen telefoon "
            "binnenkwam."
        ),
        mail_layout.Para(
            "De beller die u vorige week miste, was gratis geweest. Hij had al voor u "
            "gekozen; hij belde niet drie bedrijven tegelijk, hij belde u. Dat is het "
            "verschil tussen een lead kopen en een lead opnemen."
        ),
        mail_layout.Heading("De goedkoopste lead"),
        mail_layout.Para(
            "De goedkoopste lead die er bestaat is de telefoon die u opneemt. Elke "
            "gemiste oproep die u weet op te vangen, bespaart u de leadkosten van het "
            "platform waar die klant anders terechtkomt."
        ),
        mail_layout.Para(
            "In de volgende les: drie dingen die u deze week zelf kunt regelen, zonder "
            "ons en zonder abonnement."
        ),
        mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"),
    ]


def _blocks_3(sub: dict) -> list[mail_layout.Block]:
    return [
        mail_layout.Para(_greeting(sub)),
        mail_layout.Para(
            "Zoals beloofd: drie dingen die u deze week kunt regelen. Hier heeft u ons "
            "niet voor nodig."
        ),
        mail_layout.Steps(
            [
                "Vervang uw voicemail door een belofte. Niet \"spreek een bericht in na "
                "de piep\", maar \"wij bellen u vandaag nog terug\". En doe dat dan ook. "
                "Een beller die weet waar hij aan toe is, belt minder snel de volgende.",
                "Kies twee vaste terugbelmomenten per dag, bijvoorbeeld tien uur en drie "
                "uur. Wie snel terugbelt wint: de kans dat een aanvraag nog vrij is, "
                "daalt hard na het eerste kwartier.",
                "Turf een week lang uw gemiste oproepen. Streepje op een briefje in de "
                "bus is genoeg. Na een week weet u of dit uw probleem is, en hoe groot.",
            ]
        ),
        mail_layout.Para(
            "Wie dit doet, vangt al een flink deel op. Het enige dat deze aanpak niet "
            "oplost: de beller die geen voicemail wil en meteen iemand wil spreken. "
            "Daarover gaat de laatste les."
        ),
        mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"),
    ]


def _blocks_4(sub: dict) -> list[mail_layout.Block]:
    return [
        mail_layout.Para(_greeting(sub)),
        mail_layout.Para(
            "Laatste les. De vorige drie kon u zelf; deze gaat over wat er overblijft "
            "als u het wilt automatiseren."
        ),
        mail_layout.Heading("Wat een digitale receptionist doet"),
        mail_layout.Para(
            "Klantkraan zet een digitale receptionist op uw website en WhatsApp die dag "
            "en nacht antwoordt: hij beantwoordt vragen over uw diensten, noteert de "
            "klus met naam en adres, en plant afspraken in uw agenda. Mist u een "
            "oproep, dan krijgt de beller direct een berichtje en loopt het gesprek "
            "verder via WhatsApp."
        ),
        mail_layout.Para(
            "Hij doet zich niet voor als mens. Wie ernaar vraagt, hoort eerlijk dat het "
            "een digitale assistent is. Dat is wettelijk verplicht, en het werkt ook "
            "beter: klanten haken af op nep, niet op eerlijk."
        ),
        mail_layout.Heading("Wat het kost"),
        mail_layout.Para(
            "Vanaf 299 euro per maand, exclusief btw, maandelijks opzegbaar. Wij "
            "richten alles voor u in; u hoeft alleen te vertellen wat uw bedrijf doet. "
            "Tegenover een of twee geredde klussen per maand rekent dat zichzelf rond."
        ),
        mail_layout.Button("Probeer de demo", "https://klantkraan.nl/demo/"),
        mail_layout.Para(
            "Liever eerst iemand spreken? Antwoord op deze mail en u krijgt antwoord "
            "van een mens."
        ),
        mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"),
    ]


LESSONS: dict[int, dict] = {
    1: {
        "subject": "Les 1 van 4: de klus die naar een ander ging",
        "preheader": "Meer dan de helft van de telefoontjes wordt niet opgenomen. De rekensom.",
        "blocks": _blocks_1,
    },
    2: {
        "subject": "Les 2 van 4: wat een lead kost als u hem terugkoopt",
        "preheader": "De platformsom: ruim 200 euro leadkosten voor een klus die gratis belde.",
        "blocks": _blocks_2,
    },
    3: {
        "subject": "Les 3 van 4: drie dingen die u deze week zelf kunt regelen",
        "preheader": "Voicemail, terugbelmomenten en een briefje in de bus. Zonder abonnement.",
        "blocks": _blocks_3,
    },
    4: {
        "subject": "Les 4 van 4: als u het wilt automatiseren",
        "preheader": "Wat een digitale receptionist opvangt, en wat dat kost.",
        "blocks": _blocks_4,
    },
}


def _footer_note(email: str) -> str:
    return (
        "U ontvangt deze cursus omdat u zich heeft aangemeld via klantkraan.nl. "
        f"Afmelden: {unsubscribe_url(email)}"
    )


def render(n: int, sub: dict) -> tuple[str, str, str]:
    """(subject, text, html) for lesson `n`. Pure function of the subscriber record, so
    the CLI can preview exactly what a reader will get."""
    lesson = LESSONS[n]
    blocks = lesson["blocks"](sub)
    note = _footer_note(sub["email"])
    text = mail_layout.to_text(blocks, footer_note=note)
    html = mail_layout.to_html(
        blocks,
        subject=lesson["subject"],
        preheader=lesson["preheader"],
        lang="nl",
        footer_note=note,
    )
    return lesson["subject"], text, html


# --- schedule + sending -------------------------------------------------------------------


def due_lesson(sub: dict, now: datetime | None = None) -> int | None:
    """The one lesson this subscriber should get now, or None. Lessons go strictly in
    order and never more than one per call, whatever the backlog."""
    if sub.get("unsubscribed") or sub.get("bounced"):
        return None
    now = now or _now()
    opted = _parse(sub["opted_in"])
    lessons = sub.get("lessons", {})
    for n in LESSON_NUMBERS:
        if str(n) in lessons:
            continue
        return n if now >= opted + timedelta(days=LESSON_DAY[n]) else None
    return None


def _score_completion(sub: dict) -> str:
    """Put a course completer on the pipeline board as an inbound opt-in lead. Returns a
    one-line description of what happened, for the send report."""
    email = sub["email"]
    name = (sub.get("name") or "").strip() or email.split("@")[0]
    note = "e-mailcursus gemiste omzet afgerond (4/4 lessen ontvangen)"
    # Try the friendly slug first; a name like "Jan" can collide with an unrelated record,
    # and a note on someone else's deal is worse than an ugly slug, so on a collision that
    # is not ours (by e-mail) fall back to a slug derived from the address itself.
    for slug in (pipeline.slugify(name), pipeline.slugify(f"{name} {email.split('@')[0]}")):
        existing = pipeline.load(slug)
        if existing is None:
            pipeline.add(
                name,
                slug=slug,
                email=email,
                source="e-mailcursus",
                inbound=True,
                note=note,
            )
            return f"scored: new pipeline lead {slug}"
        if normalize(existing.get("contact", {}).get("email") or "") == email:
            pipeline.note(slug, note)
            return f"scored: noted on existing pipeline record {slug}"
    return f"scoring skipped for {email}: slug taken by another record"


def send_due(*, now: datetime | None = None, only: str | None = None, dry: bool = False) -> dict:
    """Send every due lesson (at most one per subscriber). `only` narrows to one address,
    which is how the opt-in endpoint fires lesson 1 immediately.

    Returns {"due": [(email, n)], "sent": [...], "failed": [...], "scored": [...]}.
    The ledger is written per successful send, not once at the end, so a crash mid-run
    loses at most the record of the mail Resend's Idempotency-Key already de-duplicates.
    """
    now = now or _now()
    data = load()
    subscribers = data["subscribers"]
    if only is not None:
        key = normalize(only)
        subscribers = {key: subscribers[key]} if key in subscribers else {}

    due = [(email, due_lesson(sub, now)) for email, sub in sorted(subscribers.items())]
    due = [(email, n) for email, n in due if n]
    report: dict = {"due": due, "sent": [], "failed": [], "scored": []}
    if dry or not due:
        return report

    for email, n in due:
        sub = data["subscribers"][email]
        subject, text, html = render(n, sub)
        ok = mailer.send(
            email,
            subject,
            text,
            html=html,
            idempotency_key=f"cursus-{email}-les-{n}",
            # RFC 8058 one-click: mail clients POST to the URL without showing a page.
            # The server accepts that POST next to the human confirm-button flow.
            headers={
                "List-Unsubscribe": f"<{unsubscribe_url(email)}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        )
        if not ok:
            report["failed"].append((email, n))
            continue
        sub.setdefault("lessons", {})[str(n)] = {"at": _iso(now)}
        if n == LESSON_NUMBERS[-1]:
            sub["completed"] = _iso(now)
            try:
                report["scored"].append(_score_completion(sub))
                sub["scored"] = _iso(now)
            except Exception as exc:  # noqa: BLE001 - scoring must never block sending
                report["scored"].append(f"scoring failed for {email}: {exc}")
        save(data)
        report["sent"].append((email, n))
    return report


# --- CLI ----------------------------------------------------------------------------------


def _fmt_sub(sub: dict, now: datetime) -> str:
    lessons = sub.get("lessons", {})
    progress = f"{len(lessons)}/{len(LESSON_NUMBERS)}"
    if sub.get("unsubscribed"):
        state = "afgemeld"
    elif sub.get("bounced"):
        state = "bounced"
    elif sub.get("completed"):
        state = "afgerond" + (" +pipeline" if sub.get("scored") else "")
    else:
        n = due_lesson(sub, now)
        nxt = next((m for m in LESSON_NUMBERS if str(m) not in lessons), None)
        if n:
            state = f"les {n} NU"
        elif nxt is None:
            state = "afgerond"
        else:
            when = _parse(sub["opted_in"]) + timedelta(days=LESSON_DAY[nxt])
            state = f"les {nxt} op {when.date().isoformat()}"
    name = f" ({sub['name']})" if sub.get("name") else ""
    return f"  {sub['email']}{name}  {progress}  {state}"


def cmd_board(_args: argparse.Namespace) -> int:
    data = load()
    subs = sorted(data["subscribers"].values(), key=lambda s: s["opted_in"])
    now = _now()
    active = [s for s in subs if not (s.get("unsubscribed") or s.get("bounced"))]
    done = [s for s in active if s.get("completed")]
    due = [s for s in active if due_lesson(s, now)]
    print(
        f"e-mailcursus: {len(subs)} aanmeldingen, {len(active)} actief, "
        f"{len(done)} afgerond, {len(due)} met een les klaar om te versturen"
    )
    for sub in subs:
        print(_fmt_sub(sub, now))
    if not mailer.configured():
        print("LET OP: RESEND_API_KEY ontbreekt; verzenden staat droog.")
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    report = send_due(dry=args.dry)
    if args.dry:
        if not report["due"]:
            print("niets te versturen")
        for email, n in report["due"]:
            print(f"zou versturen: les {n} -> {email}")
        return 0
    for email, n in report["sent"]:
        print(f"verstuurd: les {n} -> {email}")
    for line in report["scored"]:
        print(line)
    for email, n in report["failed"]:
        print(f"MISLUKT: les {n} -> {email}")
    if report["due"] and not mailer.configured():
        # Mirror the digest unit's rule: a sender with work and no transport must fail
        # visibly, or the timer looks green every morning while nothing goes out.
        print("cursus: RESEND_API_KEY ontbreekt en er stonden lessen klaar", file=sys.stderr)
        return 1
    return 1 if report["failed"] else 0


def cmd_preview(args: argparse.Namespace) -> int:
    sub = {"email": "voorbeeld@bedrijf.nl", "name": args.name or "Jan"}
    subject, text, _html = render(args.les, sub)
    print(f"Onderwerp: {subject}\n")
    print(text)
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    sub = add(args.email, name=args.name, source=args.source)
    print(f"aangemeld: {sub['email']} (bron: {sub['source']})")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    if stop(args.email, bounced=args.bounced):
        print(f"{'bounced' if args.bounced else 'afgemeld'}: {normalize(args.email)}")
        return 0
    print(f"onbekend adres: {normalize(args.email)}", file=sys.stderr)
    return 1


def cmd_link(args: argparse.Namespace) -> int:
    print(unsubscribe_url(args.email))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cursus", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("board", help="alle aanmeldingen + voortgang").set_defaults(fn=cmd_board)

    p = sub.add_parser("send", help="verstuur alle lessen die er klaarstaan")
    p.add_argument("--dry", action="store_true", help="alleen tonen wat er zou gaan")
    p.set_defaults(fn=cmd_send)

    p = sub.add_parser("preview", help="print een les zoals de lezer hem krijgt")
    p.add_argument("les", type=int, choices=LESSON_NUMBERS)
    p.add_argument("--name", help="voornaam in de aanhef")
    p.set_defaults(fn=cmd_preview)

    p = sub.add_parser("add", help="meld een adres handmatig aan")
    p.add_argument("email")
    p.add_argument("--name")
    p.add_argument("--source", default="handmatig")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("stop", help="afmelden (of --bounced na een DSN)")
    p.add_argument("email")
    p.add_argument("--bounced", action="store_true")
    p.set_defaults(fn=cmd_stop)

    p = sub.add_parser("link", help="print de afmeldlink van een adres")
    p.add_argument("email")
    p.set_defaults(fn=cmd_link)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
