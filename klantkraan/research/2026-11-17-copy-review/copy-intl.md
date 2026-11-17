# Copy review: English and Spanish pages (copy-intl)

Date: 2026-11-17. Scope: `apps/marketing-site/src/pages/en/**` (16 files) and `src/pages/es/**` (8 files). Every page was read as rendered (Playwright innerText at 1440 and 393, FAQ `<details>` opened) before and after editing. Text only: no code, slug, href, id, data-attribute, class or prop name was changed. All edits are uncommitted.

Summary: 294 changes in 24 files (one row per change below; shared trade-page fixes appear once per file). Spanish keeps "usted" and Spain usage (móvil, fontanero, IVA), as the pages already did. The AI disclosure lines ("You're chatting with a digital assistant.", "Está hablando con un asistente digital." and the quoted greeting on /demo/) are untouched. No price, number, guarantee, term or result was added; three overclaims were removed (see Flagged).

The "why" column is in Spanish for the Spanish rows.

## Changes per file

### src/pages/en/index.astro

| old | new | why |
|---|---|---|
| You're up a ladder, on a roof, or asleep. Your best customer has a question right now. Klantkraan's digital receptionist answers it on your site and WhatsApp, books the appointment and captures every callback request. Day and night. | You're up a ladder, on a roof or asleep, and a customer has a question right now. Klantkraan's digital receptionist answers it on your site and WhatsApp, day and night. It books the appointment and notes every callback request. | clarity / cut: "best customer" is puffery; "Day and night." fragment folded in; no Oxford comma (site style) |
| Knows your rates, services and service area. No invented prices, only what you have set. | Knows your rates, services and service area, and only quotes prices you have set. | clarity: verb sentence instead of fragment |
| Straight into your calendar, only in slots that are genuinely free. The customer picks a slot, you see it at once. | Straight into your calendar, only in free slots. The customer picks one and you see it at once. | cut "genuinely"; grammar (comma splice) |
| Can't take it right now? The receptionist notes the name, number and job. You call back the ones that matter. | When you can't pick up, the receptionist notes the name, number and job. You call back the ones that matter. | AI tell: rhetorical question |
| This is an example. Run it on your own numbers and you'll see exactly what a month of missed calls costs you. | This is an example. Run it on your own numbers to see what a month of missed calls costs you. | cut: "exactly" overstates an estimate |
| That's how every conversation starts, before anything else happens. | Every conversation starts with that line. | cut: "before anything else happens" repeats "starts" |
| From 2 August 2026 that notice is required under Article 50 of the EU AI Act. We already do it. | Article 50 of the EU AI Act requires that notice from 2 August 2026. | cut: "We already do it" repeats the line above and reads stale after the date |
| Where a voicebot is sold on "nobody can tell the difference", our receptionist simply says what it is. Your customer knows where they stand, and you risk no fine. | Some voicebots are sold on "nobody can tell the difference". Our receptionist says what it is. Your customer knows where they stand, and you risk no fine. | cut "simply"; one point per sentence |
| Cancel monthly. No annual contract, no hidden renewal; cancel by email, no notice period. | Cancel monthly by email, with no notice period. No annual contract, no hidden renewal. | cut: "cancel" said twice |
| The receptionist is the start, not the finish. It takes the front door: everything that arrives while you are working. Behind that sits the paperwork you currently do at the kitchen table at night. That is where we are heading, with the first clients. | The receptionist covers the front door: everything that arrives while you are working. Behind that sits the paperwork you now do at the kitchen table at night. That is where we are heading, together with our first clients. | AI tell ("the start, not the finish") and cut: repeats the heading |
| Quotes that follow themselves up when the customer goes quiet | Quotes that follow up by themselves when the customer goes quiet | grammar |
| Review requests at the moment the job is finished | Review requests as soon as the job is done | clarity |
| Invoice reminders for whatever stays unpaid | Reminders for unpaid invoices | cut |
| Which of these lands first is decided by the clients who are here at the time, not by us. Ask for something that is not in there and we will say so, and say when it will be. | Our clients at the time decide which of these comes first, not us. Ask for something that isn't on the list and we'll tell you so, and when it will be. | grammar / clarity: active voice, "in there" was vague |
| Try the demo and ask the receptionist a question as if you were a customer. Like it? Sign up and we take care of the rest, you build nothing. | Try the demo and ask the receptionist a question as if you were a customer. If you like it, sign up and we do the rest. You build nothing. | AI tell: rhetorical question; grammar (comma splice) |

### src/pages/en/aanmelden.astro

| old | new | why |
|---|---|---|
| [meta description] Sign your business up for Klantkraan Chat (€299) or Compleet with AI phone agent (€499 a month). We contact you within one working day and handle the full setup. | [meta description] Sign your business up for Klantkraan Chat (€299 a month) or Compleet with an AI phone agent (€499 a month), excl. VAT. We call within one working day and do the full setup. | qualifier added (excl. VAT, as in the form); "a month" on both prices; grammar |
| Let's get started | Sign up | cut: generic opener; plain verb |
| Leave your details below. We call you within one working day to go through your services, rates and calendar. We handle the setup, you build nothing. | Fill in your details below. We call you within one working day to go through your services, rates and calendar, and we do the setup. | grammar (comma splice); cut: "you build nothing" repeats "we do the setup" |
| [input title tooltip] At least 8 digits, spaces and dashes are fine | [input title tooltip] At least 8 digits; spaces and dashes are fine | grammar (comma splice) |
| Email is needed for the payment confirmation; phone is welcome too. | We need your email for the payment confirmation. A phone number helps too. | active voice |
| Email is needed for the payment confirmation; phone is welcome too. | We need your email for the payment confirmation. A phone number helps too. | active voice (same hint, set by the script) |
| data processing agreement (Dutch). | data processing agreement (in Dutch). | grammar |
| privacy policy (Dutch). | privacy policy (in Dutch). | grammar |
| Rather talk it through first? | Want to talk it through first? | grammar: Dutch-English "Rather ...?" |
| We build and connect your receptionist. Done for you; you only supply the knowledge. | We build and connect your receptionist. You only supply the information. | cut: "Done for you" repeats "We build" |
| Signing up commits you to nothing. We get in touch first to talk everything through. Cancel monthly, first month 50% off. | Cancel monthly by email, with no notice period. First month 50% off. | accuracy: "commits you to nothing / we get in touch first" sat under a "Sign up and pay" button; both plans go straight to Mollie checkout. Replaced with the cancel terms the site already states (/en/, /en/bedankt/). FLAGGED for the founder |
| Phone or email is enough; both is fine too. | Phone or email is enough. | grammar ("both is"); cut |

### src/pages/en/prijzen.astro

| old | new | why |
|---|---|---|
| Books appointments straight into your calendar and captures every lead, via website chat and WhatsApp, 24/7 in Dutch. We set the whole thing up for you. Our pick. | Answers on your website chat and WhatsApp in Dutch, day and night. Books appointments straight into your calendar and captures every lead. We set it all up for you. | cut: "Our pick" repeats the "recommended" badge (and lands in the JSON-LD); "24/7" made concrete per voice guide; one point per sentence |
| Everything in Chat, plus an AI phone agent that answers your phone 24/7 on your own Dutch number. Missed calls no longer exist. | Everything in Chat, plus an AI phone agent that answers calls on your own Dutch number, day and night. | cut: "Missed calls no longer exist" promises 100% (voice guide forbids it; the plan handles up to 5 calls at once) |
| { feature: 'Website chat on your own site (Dutch, 24/7)', chat: 'yes', compleet: 'yes' | { feature: 'Chat on your own website (Dutch, day and night)', chat: 'yes', compleet: 'yes' | cut: "website ... site"; "24/7" made concrete |
| AI phone agent on your own Dutch number', chat: '– | AI phone agent on your own Dutch number', chat: 'no | dash rule; "no" pairs with "yes" and reads aloud for screen readers |
| Included call minutes per month', chat: '– | Included call minutes per month', chat: 'no | dash rule; clarity |
| chat: '–', compleet: 'up to 5 at once' | chat: 'no', compleet: 'up to 5' | dash rule; cut: "at once" repeats "Simultaneous" |
| [meta description] Chat €299 and Compleet €499 per month. Books appointments straight into your calendar. We set the whole thing up, you build nothing. Cancel monthly. | [meta description] Chat €299 or Compleet €499 a month, excl. VAT. Books appointments straight into your calendar. We do the setup. Cancel monthly. | qualifier added (excl. VAT, as on the page); grammar (comma splice); cut |
| Rather try it first? See the demo | Prefer to try it first? See the demo | grammar: Dutch-English "Rather ...?" |
| WhatsApp applied for | WhatsApp approval arranged | clarity |
| We handle the application with Meta. You never see that process. | We apply to Meta for you. You never have to deal with it. | verb first; clarity |
| Cheaper chatbots exist. On those you are the builder, and most of them book no appointments. That difference is what you are paying for. | Cheaper chatbots exist. With those you build it yourself, and most of them can't book appointments. That difference is what you pay for. | clarity |
| Cancel monthly; cancel by email, no notice period. | Cancel monthly by email, with no notice period. | cut: "cancel" twice |
| 30-day satisfaction guarantee. Not happy? Money back. | 30-day satisfaction guarantee. If you're not happy, you get your money back. | AI tell: staccato question |
| Ready to get started? | Start today. | AI tell: "Ready to ...?"; matches the "Start today" button on /en/ |
| Rather see how it works first? Try the demo, right in your browser. | To see how it works first, try the demo in your browser. | grammar: Dutch-English "Rather ...?"; cut "right" |

### src/pages/en/demo.astro

| old | new | why |
|---|---|---|
| [meta description] Try Klantkraan's digital receptionist in your browser. Ask a question or request an appointment. Prefer a personal demo? Send a WhatsApp or email. | [meta description] Try Klantkraan's digital receptionist in your browser: ask a question or request an appointment. Or ask for a personal demo by WhatsApp or email. | AI tell: rhetorical question |
| A real, live example receptionist, right here in your browser. Ask a question or request an appointment. No obligation. | A working example receptionist, live in your browser. Ask a question or request an appointment. | cut: "real, live ... right here"; "No obligation" means nothing for a free demo |
| Chat like a customer: ask a question or request an appointment. Opens full-screen. | Chat as if you were a customer. Opens full screen. | cut: repeats the line above it on mobile |
| The receptionist answers questions about your services, rates and service area. In natural English, 24 hours a day, and only with information you've set up yourself. | The receptionist answers questions about your services, rates and service area in natural English, day and night, using only information you've set up. | grammar (fragment); "24 hours a day" made consistent with the site |
| You see live how a customer question turns into a booked appointment in the calendar. No phone tag, no back-and-forth email. | You watch a customer question turn into a booked appointment in the calendar. No phone tag, no back-and-forth email. | clarity |
| We set the receptionist up on your own services and rates and walk through it with you. You won't get a sales pitch and you're not committing to anything. | We set the receptionist up with your own services and rates and walk you through it. No sales pitch, no commitment. | cut |
| WhatsApp us now | WhatsApp us | cut: "now" |
| > Prefer email? | > Email us | a button says what it does |
| Usually a reply within one working day, straight from the owner. | You usually get a reply within one working day, straight from the owner. | grammar: no subject |
| The receptionist is an AI. Disclosing that is a legal requirement. We do it in the very first sentence of every conversation, word for word: | The receptionist is an AI, and the law requires us to say so. We do it in the first sentence of every conversation, word for word: | cut "very"; active voice |
| Prefer the numbers first? | Compare the two plans. | AI tell: rhetorical question |
| Take a look at the two plans. The demo stays one click away. | Chat and Compleet, both cancel monthly. | cut: repeated the heading and said nothing; now names the plans and the term the site states |

### src/pages/en/rekentool.astro

| old | new | why |
|---|---|---|
| Average customer value per job (€) | Average value per job (€) | cut: "customer" adds nothing |
| "Payback time" = the number of months until the plan is paid for by the revenue you win back. | "Payback time" is the number of months until the revenue you win back pays for the plan. | active voice; "=" in prose |
| Lost revenue per year = missed calls × customer value × 33% conversion. So we only count 1 in 3 missed calls as a lost job; without a callback system, most callers give up. | Lost revenue per year = missed calls × value per job × 33% conversion. We only count 1 in 3 missed calls as a lost job, although without a callback system most callers give up. | clarity: the reasoning read backwards; label matches the form ("value per job") |
| The bigger your pile of missed jobs, the faster Klantkraan pays for itself. | The more jobs you miss, the faster Klantkraan pays for itself. | clarity |
| And what does a job through Werkspot cost? | What a job through Werkspot costs | AI tell: rhetorical question as heading |
| channel, where every caller simply gets answered. | channel, where every caller gets an answer. | cut: "simply" |
| Your own channel also grows in value: every review, every returning customer and every referral belongs to you, not to the platform. | Your own channel also grows in value: reviews, returning customers and referrals belong to you, not to the platform. | AI tell: "every..., every..., every..." triad |

### src/pages/en/over.astro

| old | new | why |
|---|---|---|
| Customer data lives with Cloudflare EU + Neon EU + Hetzner FSN1. | Customer data is stored with Cloudflare EU, Neon EU and Hetzner FSN1. | clarity: "+" in prose |
| No vendor lock-in, no annual contract by default. You stay because it works, not because you have to. | No vendor lock-in, no annual contract by default. | AI tell: "because X, not because Y" slogan with no fact |
| BV. No outside investors, no VC pressure, no growth figures that come before customer quality. | BV. No outside investors and no pressure to put growth before quality. | AI tell: triad; "no outside investors" already in the hero |
| trades: plumbers, roofers, electricians, installation engineers, contractors, painters. | trades: plumbers, roofers, electricians, heating engineers, contractors and painters. | terminology: "heating engineers" as on /en/installateur/ |
| Klantkraan grew out of a simple observation: industry estimates put missed calls at around 28% for the average Dutch plumber, roofer or installation engineer. Not out of unwillingness. They're up on the roof, on the ladder, or with another customer. And roughly 1 in 3 of those missed calls would have become a paying job, at around €450 apiece, that now goes to the competition. | Klantkraan started with one figure: industry estimates put missed calls at around 28% for the average Dutch plumber, roofer or heating engineer. Not out of unwillingness: they're up on a roof, on a ladder or with another customer. Roughly 1 in 3 of those missed calls would have become a paying job, at around €450 apiece, that now goes to the competition. | clarity; terminology; no Oxford comma |
| The solutions that existed didn't feel right. Too expensive (€899 setup + €199/mo), twelve-month contracts, or one of those American packages that doesn't do call-out charges and doesn't know what an emergency rate is. We wanted to build something that sounds like it belongs to the business: fluent Dutch, knows what a water heater is, polite but to the point. | The existing options didn't fit. They were too expensive (€899 setup plus €199 a month), tied you to a twelve-month contract, or were American packages that know nothing about call-out charges or emergency rates. We wanted something that sounds like part of the business: fluent Dutch, knows what a water heater is, polite but to the point. | grammar: the list had no verb; cut |
| Klantkraan is exactly that: a digital receptionist via website chat and WhatsApp that answers questions, books appointments and captures leads, with an AI phone agent on your own number on top. Done-for-you setup, cancel monthly. Built by someone who runs their own IT business, hosted in Europe. | Klantkraan is that: a digital receptionist on website chat and WhatsApp that answers questions, books appointments and captures leads, plus an AI phone agent on your own number in the Compleet plan. Done-for-you setup, cancel monthly. | cut: last sentence repeats the hero (and said "Europe" where the hero says "the Netherlands"); qualifier added that the phone agent is the Compleet plan, as /en/prijzen/ states |
| Questions that don't need a demo? Send a WhatsApp or an email. Usually a reply within one working day, straight from the owner. | For questions that don't need a demo, send a WhatsApp or an email. You usually get a reply within one working day, straight from the owner. | AI tell: rhetorical question; grammar (no subject) |

### src/pages/en/voor-wie.astro

| old | new | why |
|---|---|---|
| Klantkraan speaks the language of your trade. Trial classes and memberships for the gym. Call-out charges and emergency rates for the plumber. Square-metre pricing and colour samples for the painter. | Klantkraan speaks the language of your trade: call-out charges and emergency rates for a plumber, trial classes and memberships for a gym. | AI tell: staccato fragments in a forced three; two examples carry the point |
| See the solution for {b.labelPluralEn.toLowerCase() | See how it works for {b.labelPluralEn.toLowerCase() | clarity: "solution" is sales jargon |
| Klantkraan works for any business where customer questions and appointments come in, from carpenters, landscapers and glaziers to hairdressers, physios and driving schools. In a short intake we capture your services, rates and house rules. After that the receptionist answers the way you would yourself. | Klantkraan works for any business that gets customer questions and appointments, from carpenters and glaziers to hairdressers and driving schools. In a short intake we note your services, rates and house rules. After that the receptionist answers the way you would. | cut: two examples per end of the range are enough; "yourself" redundant |

### src/pages/en/bedankt.astro

| old | new | why |
|---|---|---|
| Your payment was processed by Mollie. As soon as it clears, your subscription starts automatically and we get to work for you. | Mollie has processed your payment. As soon as it clears, your subscription starts automatically and we get to work. | active voice; cut "for you" |
| We build and connect your receptionist. Done for you; you only supply the knowledge. | We build and connect your receptionist. You only supply the information. | cut: "Done for you" repeats "We build" |
| Cancel monthly; cancel by email, no notice period. | Cancel monthly by email, with no notice period. | cut: "cancel" twice |
| No problem: your payment link stays valid, so you can try again later. | Your payment link stays valid, so you can try again later. | cut: filler opener |
| and we'll sort it out together. | and we'll sort it out. | cut: "together" |

### src/pages/en/loodgieters.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't have to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: "You don't have to do a thing" repeats "we install for you"; "your own" x3 |
| That's exactly what this is built for. The receptionist answers | The receptionist answers | cut: filler opener |
| That isn't a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| keep chat conversations for 30 days, unless you want less. The full supplier list is published openly in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | grammar ("want less"); cut "published openly" |
| For anyone who'd rather pay 6 or 12 months up front there's a discount (15% and 20% respectively), but that's a choice, not the default. | If you pay 6 or 12 months up front, you get 15% or 20% off. | AI tell ("a choice, not the default"); cut "respectively" |
| Under a sink right now? Our digital receptionist answers the customer's question on your website and via WhatsApp, with your call-out charge and emergency rate ready to hand. Evenings, weekends, holidays. Same story. Appointments and callback requests come with the same subscription. | While you're under a sink, our digital receptionist answers the customer's question on your website and via WhatsApp, with your call-out charge and emergency rate to hand. Evenings, weekends and holidays too. Appointments and callback requests come in the same subscription. | AI tell: rhetorical question and staccato ("Same story."); cut |
| Miss 10 calls a week at €450 each? That's <strong | Miss 10 calls a week at €450 each and you lose <strong | AI tell: question-and-reveal; one sentence |
| >over €77,000 in lost revenue a year</strong | >over €77,000 in revenue a year</strong | cut: "lost" now in "you lose" |
| Ready to stop missing jobs? | Try it as your customer would. | AI tell: "Ready to ...?" |
| Try the live demo. In one conversation you'll see how the receptionist answers a question about call-out charges and puts an appointment in the calendar. | One conversation in the live demo shows the receptionist answering a question about call-out charges and putting an appointment in the calendar. | cut: "Try the live demo" repeats the button |

### src/pages/en/elektricien.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't have to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: "You don't have to do a thing" repeats "we install for you"; "your own" x3 |
| That's exactly what this is built for. The receptionist answers | The receptionist answers | cut: filler opener |
| That isn't a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| keep chat conversations for 30 days, unless you'd prefer shorter. The full supplier list is public in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | consistency across trade pages |
| If you'd rather pay 6 or 12 months up front there's a discount (15% and 20% respectively). | If you pay 6 or 12 months up front, you get 15% or 20% off. | cut "respectively"; consistency |
| books appointments and captures leads, 24/7." | books appointments and captures leads, day and night." | "24/7" made concrete (voice guide) |
| A digital receptionist on your website and WhatsApp that explains to your customer what a short-circuit emergency rate is. Or an EV charge-point extra. It answers questions 24/7. | A digital receptionist on your website and WhatsApp that explains your short-circuit emergency rate or EV charge-point extra to a customer. It answers questions day and night. | grammar (fragment); "24/7" made concrete |
| in natural, fluent conversation, after 5pm and at weekends too. It only quotes your own short-circuit emergency rate, hourly rate and weekend surcharge. Never a price you haven't set in advance. | in natural conversation, after 5pm and at weekends too. It only quotes your own short-circuit emergency rate, hourly rate and weekend surcharge, never a price you haven't set in advance. | cut "fluent" (doubles "natural"); fragment joined |
| Power cut after closing time? The receptionist takes the report | When a power cut comes in after closing time, the receptionist takes the report | AI tell: rhetorical question |
| Three modules for one monthly price. Not for the big installation firms. For the electrician with two to eight engineers. | Three modules for one monthly price. Built for the electrician with two to eight engineers, not the big installation firms. | AI tell: "Not for X. For Y." staccato |
| Miss 8 calls a week at €375? That's <strong | Miss 8 calls a week at €375 each and you lose <strong | AI tell: question-and-reveal |
| >over €51,000 of lost revenue a year</strong | >over €51,000 in revenue a year</strong | cut; grammar ("of") |
| Ready to stop missing short-circuit emergencies? | Try it as your customer would. | AI tell: "Ready to ...?" |
| Try the live demo. You'll see how it quotes your short-circuit emergency rate and what it does when someone asks a question about an EV charge point. | Ask the live demo what your customers ask, such as an emergency rate or an EV charge point. It runs on an example business; your own receptionist quotes your rates. | accuracy: the EN demo is an example air-conditioning business, so it cannot quote "your" short-circuit rate; wording now matches /en/demo/ ("This is an example business") |

### src/pages/en/schilder.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't have to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: "You don't have to do a thing" repeats "we install for you"; "your own" x3 |
| That's exactly what this is built for. The receptionist answers | The receptionist answers | cut: filler opener |
| That isn't a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| The receptionist handles conversations in parallel. No queue. Ten customers | The receptionist handles conversations in parallel, so there is no queue. Ten customers | AI tell: staccato fragment |
| keep chat conversations for 30 days, unless you want them kept for less. The full supplier list is published openly in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | cut; consistency |
| For anyone who would rather pay 6 or 12 months up front there's a discount (15% and 20% respectively). | If you pay 6 or 12 months up front, you get 15% or 20% off. | cut; consistency |
| books appointments, 24/7." | books appointments, day and night." | "24/7" made concrete |
| It catches the evening requests you miss now while you're up on the scaffolding. And the spring peak without you hiring extra people. | It catches the evening requests you now miss while you're up on the scaffolding, and handles the spring peak without extra staff. | grammar: the last sentence had no verb |
| A homeowner asks for a quote after hours? The receptionist catches the request | When a homeowner asks for a quote after hours, the receptionist catches the request | AI tell: rhetorical question |
| What if five customers send a request at the same time during the spring season? | What if several customers send a request at once during the spring peak? | consistency: the question said five, the answer says ten; "spring peak" as elsewhere on the page |
| Klantkraan Chat is €299 a month. One spring job you currently lose to the evening callers pays for the whole subscription. | Klantkraan Chat is €299 a month. One spring job from an evening request you now miss pays for the subscription. | clarity: "lose to the evening callers" read as losing to the callers; cut "whole" |
| Miss 5 quote requests a month at €2,500 each? That's <strong | Miss 5 quote requests a month at €2,500 each and you lose <strong | AI tell: question-and-reveal |
| >around €50,000 in lost revenue a year</strong | >around €50,000 in revenue a year</strong | cut |
| Ready for the spring season? | Get set up before the spring peak. | AI tell: "Ready for ...?" |
| Try the live demo. You'll see how it tells a per-m² question and a colour-sample question apart, and what it does when someone asks about spray work. | Ask the live demo a per-m² question or a colour-sample question. It runs on an example business; your own receptionist quotes your rates. | accuracy: the EN demo is an example air-conditioning business, not a painter |
| Ten customers can chat or WhatsApp at the same time | Ten customers can chat or message at the same time | consistency: same wording as the other trade pages |

### src/pages/en/installateur.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't need to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: repeats "we install for you"; "your own" x3 |
| That's exactly what this is built for. The receptionist answers | The receptionist answers | cut: filler opener |
| That's not a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| The receptionist handles conversations in parallel. No queue. Ten customers | The receptionist handles conversations in parallel, so there is no queue. Ten customers | AI tell: staccato fragment |
| keep chat conversations for 30 days, unless you'd prefer less. The full supplier list is published openly in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | grammar ("prefer less"); cut |
| For anyone who'd rather pay 6 or 12 months up front there's a discount (15% and 20% respectively). | If you pay 6 or 12 months up front, you get 15% or 20% off. | cut; consistency |
| A digital receptionist on your website and WhatsApp that spots a boiler breakdown and won't mistake it for a scheduling question about the annual service. Catches the January peak and the October servicing rush. Evenings and weekends included. | A digital receptionist on your website and WhatsApp that tells a boiler breakdown from a question about the annual service. It catches the January peak and the October servicing rush, evenings and weekends included. | cut; grammar (fragments) |
| Boiler breakdown during a cold snap? The receptionist takes the message | When a boiler breaks down in a cold snap, the receptionist takes the message | AI tell: rhetorical question |
| Built for the heating engineer who no longer wants to leave the January peak to their partner. | Built for the heating engineer who no longer wants to leave the phone to their partner in the January peak. | clarity: what the partner is left with |
| Miss 7 calls a week at €340? That's <strong | Miss 7 calls a week at €340 each and you lose <strong | AI tell: question-and-reveal |
| >around €41,000 in lost revenue a year</strong | >around €41,000 in revenue a year</strong | cut |
| Everything that comes in after that is revenue. And the customer isn't sat in a cold house for three hours. | Everything after that is extra revenue, and your customer isn't left in a cold house for three hours. | grammar ("isn't sat"); cut |
| Ready for the next heating season? | Get set up before the next heating season. | AI tell: "Ready for ...?" |
| Try the live demo. After that you'll know whether it spots a boiler breakdown and how it separates one from a question about the annual service. | In the live demo, report a breakdown, then ask about a routine service. You'll see how it tells the two apart. | verb first; cut. Kept generic because the EN demo is an air-conditioning business |

### src/pages/en/aannemer.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't have to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: "You don't have to do a thing" repeats "we install for you"; "your own" x3 |
| That's exactly what this is built for. The receptionist answers | The receptionist answers | cut: filler opener |
| That isn't a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| The receptionist handles conversations in parallel. No queue. Ten customers | The receptionist handles conversations in parallel, so there is no queue. Ten customers | AI tell: staccato fragment |
| keep chat conversations for 30 days, unless you want a shorter period. The full supplier list is public in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | cut; consistency |
| If you'd rather pay 6 or 12 months up front there's a discount (15% and 20% respectively). | If you pay 6 or 12 months up front, you get 15% or 20% off. | cut; consistency |
| Keeps quote requests, variations and suppliers apart. Someone asks about a renovation at 19:30 while you're still on site? The digital receptionist answers them on your website and via WhatsApp. No more missed enquiries. | A digital receptionist that keeps quote requests, variations and suppliers apart. When someone asks about a renovation at 19:30 while you're still on site, it answers them on your website and via WhatsApp. | grammar (no subject); AI tell (rhetorical question); cut "No more missed enquiries" (promises 100%, voice guide forbids it) |
| A client gets in touch during a site visit? The receptionist catches the enquiry | When a client gets in touch during a site visit, the receptionist catches the enquiry | AI tell: rhetorical question |
| Unknown questions are never made up; instead the customer gets a callback request. | Answers it doesn't have are never made up; instead the customer gets a callback request. | logic: questions are not "made up", answers are |
| For the contractor who's on site when their best prospect calls. | Built for the contractor who's on site when the best prospect calls. | grammar (fragment); same pattern as the other trade pages |
| Miss 2 quote requests a month at €12,000 each? That's <strong | Miss 2 quote requests a month at €12,000 each and you lose <strong | AI tell: question-and-reveal |
| >around €95,000 in lost revenue a year</strong | >around €95,000 in revenue a year</strong | cut |
| After that, every missed prospect you win back is pure profit. | After that, every prospect you win back is extra revenue. | accuracy: a renovation is revenue, not "pure profit"; cut "missed" |
| Ready to stop missing renovation enquiries? | Try it as your client would. | AI tell: "Ready to ...?" |
| Try the live demo. Then you'll know how it keeps quote requests, variation queries and suppliers apart. And how that lands in your WhatsApp. | Ask the live demo what your clients ask. It runs on an example business; your own receptionist is set up with your services and rates. | accuracy: the EN demo is an example air-conditioning business and shows no WhatsApp summary |

### src/pages/en/sportscholen.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script that we install for you. You don't have to do a thing. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: "You don't have to do a thing" repeats "we install for you"; "your own" x3 |
| That isn't a marketing choice but a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X but Y" |
| keep chat conversations for 30 days, unless you want shorter. The full supplier list is public in our sub-processor register. | keep chat conversations for 30 days, or shorter if you prefer. The full supplier list is public in our sub-processor register. | grammar ("want shorter") |
| For anyone who prefers to pay 6 or 12 months up front there's a discount (15% and 20% respectively), but that's a choice, not the default. | If you pay 6 or 12 months up front, you get 15% or 20% off. | AI tell ("a choice, not the default"); cut |
| On the floor teaching a class? Then our digital receptionist answers the question about memberships or the trial class, on your website and via WhatsApp, with your schedule and rates to hand. Evenings, weekends, public holidays. The trial class goes straight into your calendar. | While you're on the floor teaching a class, our digital receptionist answers questions about memberships and trial classes on your website and via WhatsApp, with your schedule and rates to hand. Evenings, weekends and public holidays too. Trial classes go straight into your calendar. | AI tell: rhetorical question; staccato list |
| books the trial class and lets your team do what they're good at: the floor. | books the trial class and leaves your team free for the gym floor. | AI tell: colon reveal |
| It catches them neatly: the assistant notes the request, books a call if needed and passes it straight to you. Decisions about memberships stay with your team. The assistant only makes sure the request never gets left. | It notes the request, books a call if needed and passes it straight to you. Decisions about memberships stay with your team; the assistant only makes sure no request gets lost. | AI tell: colon reveal; grammar ("never gets left") |
| Leave 4 trial-class requests a month unanswered, at €480 yearly value each? That's over €23,000 in lost revenue a year. | Leave 4 trial-class requests a month unanswered, at €480 a year each, and you lose over €23,000 in revenue a year. | AI tell: question-and-reveal |
| Ready to stop missing trial classes? | Try it as a new member would. | AI tell: "Ready to ...?" |
| Try the live demo of a gym receptionist. In one conversation you'll see how a question about a membership ends as a booked trial class in the calendar. | Ask the live demo a question and book an appointment. It runs on an example business; your own receptionist is set up with your classes and memberships. | accuracy: /en/demo/ is an example air-conditioning business, not "a gym receptionist" |

### src/pages/en/air-conditioning.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| With one small script we install for you. You don't lift a finger. We connect the WhatsApp channel in the same done-for-you setup. You keep your own site, your own number and your own branding. | With one small script that we install for you. We connect WhatsApp in the same setup. You keep your own site, number and branding. | cut: repeats "we install for you"; "your own" x3 |
| That's exactly what this is for. The receptionist answers | The receptionist answers | cut: filler opener |
| This isn't a marketing choice. It's a legal requirement under article 50 of the EU AI Act. The disclosure always stays on. | Article 50 of the EU AI Act requires it, and the disclosure always stays on. | AI tell: "not X. It's Y" |
| The receptionist handles conversations in parallel. No queue. Ten customers | The receptionist handles conversations in parallel, so there is no queue. Ten customers | AI tell: staccato fragment |
| If you'd rather pay 6 or 12 months up front there's a discount (15% and 20% respectively). | If you pay 6 or 12 months up front, you get 15% or 20% off. | cut; consistency |
| [meta description] Digital receptionist for air-conditioning & HVAC firms: answers no-cooling calls, quotes rates, books installs and services on WhatsApp, 24/7. Cancel monthly. | [meta description] Digital receptionist for air-conditioning and HVAC firms: answers no-cooling enquiries, quotes your rates and books jobs on your site and WhatsApp, day and night. Cancel monthly. | accuracy: it answers chat and WhatsApp, not calls, and the website was missing; "24/7" made concrete |
| A digital receptionist on your website and WhatsApp that recognises an urgent no-cooling call and doesn't confuse it with a routine service booking. Catches the summer rush and the after-hours enquiries. Evenings and weekends included. | A digital receptionist on your website and WhatsApp that tells an urgent no-cooling call from a routine service booking. It catches the summer rush and after-hours enquiries, evenings and weekends included. | cut; grammar (fragments) |
| A unit down in a heatwave? The receptionist captures it and drops it straight onto your phone as a message | When a unit goes down in a heatwave, the receptionist takes the details and sends them straight to your phone as a message | AI tell: rhetorical question |
| Miss 5 enquiries a week at €450? That's <strong | Miss 5 enquiries a week at €450 each and you lose <strong | AI tell: question-and-reveal |
| >around €39,000 in lost revenue a year</strong | >around €39,000 in revenue a year</strong | cut |
| Amounts excl. 21% VAT. Illustrative example based on | Amounts exclude 21% VAT. Example based on | cut "Illustrative" (doubles "example"); same wording as the other trade pages |
| Ready for the next heatwave? | Get set up before the next heatwave. | AI tell: "Ready for ...?" |
| Try the live demo. Then you'll know whether it recognises an urgent no-cooling call and how it tells that apart from a routine service question. | In the live demo, report a unit that has stopped cooling, then ask about a routine service. You'll see how it tells the two apart. | verb first; cut |

### src/pages/en/dakdekkers.astro

| old | new | why |
|---|---|---|
| Disclosure on by default | Disclosure always on | accuracy: "on by default" implies it can be switched off; every other line on the site says it cannot |
| Three modules. One monthly price. | Three modules for one monthly price. | AI tell: staccato fragments |
| The receptionist handles conversations in parallel. No queue. Ten customers | The receptionist handles conversations in parallel, so there is no queue. Ten customers | AI tell: staccato fragment |
| books inspections and captures leads, 24/7." | books inspections and captures leads, day and night." | "24/7" made concrete |
| A storm protocol that escalates emergency leaks straight to your phone. A 24/7 emergency channel that answers naturally. Inspection and quote appointments booked straight into your calendar. | A storm protocol sends emergency leaks straight to your phone, day and night. Inspection and quote appointments go straight into your calendar. | AI tell: three verbless fragments; cut |
| On your website and WhatsApp, the receptionist tells the difference between a quote request and an emergency leak. For an emergency: an instant alert on your phone, evenings and weekends included. Simultaneous conversations run in parallel. No queue. | On your website and WhatsApp, the receptionist tells a quote request from an emergency leak. An emergency means an instant alert on your phone, evenings and weekends included. Conversations run in parallel, so there is no queue. | AI tell: colon reveal and staccato; cut "Simultaneous" (doubles "in parallel") |
| Yes, from the very first line. The assistant states clearly that your customer is chatting with a digital assistant, in line with article 50 of the EU AI Act. The experience stays professional and natural. Read the full | Yes, from the first line. The assistant tells your customer they're chatting with a digital assistant, as article 50 of the EU AI Act requires. Read the full | cut: "very", "clearly" and a sentence with no fact |
| You keep your current number, nothing is ported or forwarded. | You keep your current number; nothing is ported or forwarded. | grammar (comma splice) |
| Three modules for one monthly price. Written after an evening spent listening in with a roofer in Utrecht after storm Pia. | Three modules for one monthly price. We wrote them after storm Pia, having spent an evening listening in with a roofer in Utrecht. | grammar: "after ... after"; no subject |
| Three customers call at once with a leak. You're at a birthday party, or you're already asleep. What happens now? And with Klantkraan? | Three customers call at once with a leak. You're at a birthday party or already asleep. | AI tell: rhetorical questions; the two cards below already say "Without" and "With Klantkraan" |
| Three calls, three resolutions. | Three calls, all three handled. | clarity: "resolutions" is the wrong word |
| The AI takes all three in parallel, in natural conversation, with AI disclosure. | The AI takes all three in parallel, each with the AI disclosure. | cut |
| Monday: three review requests sent, three customers helped, zero missed jobs. | Monday: three customers helped, zero missed jobs. | accuracy: review requests are listed under "What we are building" on /en/ (not available yet). FLAGGED |
| Ready for the next storm season? | Get set up before the next storm. | AI tell: "Ready for ...?" |
| One subscription that takes the storm peak. No annual contract. We set everything up for you. First month half price. | One subscription handles the storm peak. We set everything up for you, with no annual contract and the first month at half price. | AI tell: four staccato fragments |

### src/pages/es/index.astro

| old | new | why |
|---|---|---|
| Está en lo alto de una escalera, en un tejado, o durmiendo. Su mejor cliente tiene una pregunta ahora mismo. La recepcionista digital de Klantkraan la responde en su web y por WhatsApp, agenda la cita y anota cada solicitud de llamada. De día y de noche. | Está en lo alto de una escalera, en un tejado o durmiendo, y un cliente tiene una pregunta ahora mismo. La recepcionista digital de Klantkraan la responde en su web y por WhatsApp, de día y de noche. Agenda la cita y anota cada solicitud de llamada. | gramática (sin coma ante "o"); corte: "su mejor cliente" es relleno; fragmento final integrado |
| Conoce sus tarifas, servicios y zona de trabajo. Sin precios inventados, solo lo que usted ha configurado. | Conoce sus tarifas, servicios y zona de trabajo, y solo da los precios que usted ha fijado. | claridad: frase con verbo en lugar de fragmento |
| Directo en su calendario, solo en horas que están realmente libres. El cliente elige un hueco y usted lo ve al instante. | Directo en su calendario, solo en huecos libres. El cliente elige uno y usted lo ve al instante. | corte: "realmente" |
| ¿No puede atender ahora? La recepcionista anota el nombre, el número y el trabajo. Usted devuelve la llamada a quien de verdad importa. | Cuando usted no puede atender, la recepcionista anota el nombre, el número y el trabajo. Usted devuelve la llamada a quien de verdad importa. | AI tell: pregunta retórica |
| Esto es un ejemplo. Hágalo con sus propios números y verá exactamente lo que le cuesta un mes de llamadas perdidas. | Esto es un ejemplo. Calcúlelo con sus propias cifras y verá lo que le cuesta un mes de llamadas perdidas. | calco del inglés ("hágalo con sus números"); corte: "exactamente" exagera una estimación |
| Hágalo con sus propios números | Calcúlelo con sus propias cifras | calco del inglés |
| Honestos con la IA | Honestos sobre la IA | gramática: "con la IA" significa "hacia la IA" |
| Así empieza cada conversación, antes de cualquier otra cosa. | Cada conversación empieza con esa frase. | corte: repetición |
| Desde el 2 de agosto de 2026 ese aviso es obligatorio según el artículo 50 del Reglamento de IA de la UE. Nosotros ya lo hacemos. | El artículo 50 del Reglamento de IA de la UE exige ese aviso desde el 2 de agosto de 2026. | corte: "ya lo hacemos" repite la línea anterior y envejece tras la fecha |
| Donde un robot de voz se vende con "nadie nota la diferencia", nuestra recepcionista dice sin rodeos lo que es. Su cliente sabe con quién habla y usted no se arriesga a una multa. | Hay robots de voz que se venden con un "nadie nota la diferencia". Nuestra recepcionista dice lo que es. Su cliente sabe con quién habla y usted no se arriesga a una multa. | claridad: una idea por frase |
| En un día laborable le llamamos para repasar sus servicios, tarifas y calendario. Usted no construye nada. | En un día laborable le llamamos para repasar sus servicios, tarifas y calendario. Usted no tiene que montar nada. | anglicismo: "construir" software |
| Cancelación mensual. Sin contrato anual ni renovación oculta; se cancela por correo, sin preaviso. | Puede cancelar cada mes con un correo, sin preaviso. Sin contrato anual ni renovación oculta. | corte: "cancelar" dos veces |
| La recepcionista es el principio, no el final. Se ocupa de la puerta: todo lo que entra mientras usted trabaja. Detrás está el papeleo que ahora hace de noche en la mesa de la cocina. Hacia ahí vamos, junto con los primeros clientes. | La recepcionista se ocupa de la puerta: todo lo que entra mientras usted trabaja. Detrás está el papeleo que ahora hace de noche en la mesa de la cocina. Hacia ahí vamos, junto con nuestros primeros clientes. | AI tell ("el principio, no el final") y corte: repite el título |
| Recoge solicitudes de devolución de llamada con nombre, número y trabajo | Anota solicitudes de llamada con nombre, número y trabajo | terminología: igual que el resto de la página ("solicitud de llamada") |
| Presupuestos que se recuerdan solos cuando el cliente no responde | Presupuestos que hacen su propio seguimiento cuando el cliente no responde | claridad: "se recuerdan solos" no se entiende |
| Peticiones de reseña justo cuando el trabajo acaba de terminar | Peticiones de reseña en cuanto termina el trabajo | corte: "justo cuando ... acaba de" |
| Recordatorios de factura para lo que sigue pendiente | Recordatorios de facturas pendientes | corte |
| Cuál de estas llega primero lo deciden los clientes que haya entonces, no nosotros. ¿Pide algo que no está incluido? Se lo decimos, y le decimos cuándo lo estará. | Qué llega primero lo deciden los clientes que tengamos entonces, no nosotros. Si pide algo que no está en la lista, se lo decimos, y también cuándo estará. | AI tell: pregunta retórica; corte: "le decimos" dos veces |
| Pruebe la demo y hágale una pregunta a la recepcionista como si fuera un cliente. ¿Le convence? Dese de alta y nosotros nos encargamos del resto, usted no construye nada. | Pruebe la demo y hágale una pregunta a la recepcionista como si fuera un cliente. Si le convence, dese de alta y nosotros nos encargamos del resto. | AI tell: pregunta retórica; corte: "usted no construye nada" repite "nos encargamos del resto" |

### src/pages/es/aanmelden.astro

| old | new | why |
|---|---|---|
| [meta description] Dé de alta su negocio en Klantkraan Chat (299 €) o Compleet con agente telefónico de IA (499 € al mes). Le contactamos en un día laborable y nos encargamos de toda la instalación. | [meta description] Dé de alta su negocio en Klantkraan Chat (299 € al mes) o Compleet con agente telefónico de IA (499 € al mes), IVA no incluido. Le llamamos en un día laborable y nos encargamos de toda la instalación. | calificador añadido (IVA no incluido, como en el formulario); "al mes" en ambos precios |
| Manos a la obra | Dese de alta | claridad: el título dice lo que se hace aquí; igual que el paso 1 de /es/ |
| Deje sus datos abajo. Le llamamos en un día laborable para repasar sus servicios, tarifas y calendario. Nosotros montamos todo; usted no tiene que construir nada. | Rellene sus datos abajo. Le llamamos en un día laborable para repasar sus servicios, tarifas y calendario, y nosotros nos encargamos de la instalación. | corte; anglicismo "construir" |
| [input title tooltip] Al menos 8 cifras, se admiten espacios y guiones | [input title tooltip] Al menos 8 cifras; se admiten espacios y guiones | puntuación |
| El correo es necesario para la confirmación del pago; el teléfono es bienvenido. | Necesitamos su correo para la confirmación del pago. El teléfono también ayuda. | voz activa; "el teléfono es bienvenido" es calco |
| El correo es necesario para la confirmación del pago; el teléfono es bienvenido. | Necesitamos su correo para la confirmación del pago. El teléfono también ayuda. | voz activa (mismo texto, lo pone el script) |
| acuerdo de tratamiento de datos | contrato de tratamiento de datos | terminología: "contrato de tratamiento de datos" como en /es/over/ y el pie |
| Marque la casilla para aceptar las condiciones y el acuerdo de tratamiento de datos. | Marque la casilla para aceptar las condiciones y el contrato de tratamiento de datos. | terminología |
| El pago se realiza de forma segura a través de Mollie. | Pagará de forma segura a través de Mollie. | voz activa |
| Solicitud recibida | Alta recibida | coherencia: es un alta, no una solicitud |
| Montamos y conectamos su recepcionista. Llave en mano; usted solo aporta el conocimiento. | Montamos y conectamos su recepcionista. Usted solo aporta la información. | corte: "Llave en mano" repite "Montamos" |
| da el visto bueno y la recepcionista entra en marcha en su web y WhatsApp. | da el visto bueno y la recepcionista se pone en marcha en su web y WhatsApp. | gramática: "se pone en marcha" |
| Darse de alta no le compromete a nada. Primero hablamos con usted y lo repasamos todo. Cancelación mensual, primer mes al 50%. | Puede cancelar cada mes con un correo, sin preaviso. Primer mes al 50%. | precisión: "no le compromete a nada / primero hablamos" estaba bajo un botón "Darme de alta y pagar"; ambos planes van directos al pago en Mollie. Sustituido por las condiciones de cancelación que el sitio ya indica. SEÑALADO al fundador |
| Con teléfono o correo basta; ambos también vale. | Basta con teléfono o correo. | gramática ("ambos también vale"); corte |

### src/pages/es/prijzen.astro

| old | new | why |
|---|---|---|
| Agenda citas directamente en su calendario y capta cada cliente, por chat web y WhatsApp, 24/7. Se lo dejamos montado entero. Nuestra recomendación. | Responde por chat web y WhatsApp, de día y de noche. Agenda citas directamente en su calendario y capta cada cliente. Lo dejamos todo montado. | corte: "Nuestra recomendación" repite la etiqueta "recomendado"; "24/7" concreto; una idea por frase |
| Todo lo de Chat, más un agente telefónico con IA que atiende su teléfono 24/7 en su propio número. Las llamadas perdidas dejan de existir. | Todo lo de Chat, más un agente telefónico con IA que atiende las llamadas en su propio número, de día y de noche. | corte: "Las llamadas perdidas dejan de existir" promete el 100% (prohibido en la guía de voz; el plan atiende hasta 5 llamadas a la vez) |
| Empezar con Chat | Empiece con Chat | coherencia: imperativo de usted como "Empiece hoy" y "Pruebe la demo" |
| Empezar con Compleet | Empiece con Compleet | coherencia: imperativo de usted |
| { feature: 'Chat en su propia web (24/7)', chat: 'sí', compleet: 'sí' | { feature: 'Chat en su propia web (de día y de noche)', chat: 'sí', compleet: 'sí' | "24/7" concreto (guía de voz) |
| Agente telefónico con IA en su propio número', chat: '– | Agente telefónico con IA en su propio número', chat: 'no | regla de guiones; "no" frente a "sí" |
| Minutos de llamada incluidos al mes', chat: '– | Minutos de llamada incluidos al mes', chat: 'no | regla de guiones |
| chat: '–', compleet: 'hasta 5 a la vez' | chat: 'no', compleet: 'hasta 5' | regla de guiones; corte: "a la vez" repite "simultáneas" |
| [meta description] Chat 299 € y Compleet 499 € al mes. Agenda citas directamente en su calendario. Se lo dejamos montado entero, usted no monta nada. Cancelación mensual. | [meta description] Chat 299 € o Compleet 499 € al mes, IVA no incluido. Agenda citas directamente en su calendario. Lo montamos nosotros. Cancelación mensual. | calificador añadido (IVA no incluido, como en la página); corte |
| Instalación única desde 249 € (gratis para clientes piloto). | Instalación desde 249 €, pago único (gratis para clientes piloto). | claridad: "instalación única" se lee como "instalación singular" |
| Convertirlo en un recepcionista que conoce | Convertirlo en una recepcionista que conoce | coherencia: "la recepcionista" en todo el sitio |
| Para que la cita entre directamente, y no como una nota en un buzón de correo. | Para que la cita entre directamente en él, y no como una nota en su correo. | claridad |
| WhatsApp solicitado | Alta de WhatsApp tramitada | claridad |
| La solicitud ante Meta la gestionamos nosotros. Usted no la ve. | Tramitamos la solicitud ante Meta. Usted no tiene que hacer nada. | verbo delante; claridad |
| ¿Tarifas nuevas o un servicio nuevo? Un correo y lo ajustamos. Siempre. | ¿Tarifas nuevas o un servicio nuevo? Un correo y lo ajustamos, mientras siga con nosotros. | precisión: igual que la versión inglesa ("for as long as you stay"); "Siempre." suelto |
| Hay chatbots más baratos. En esos el que monta es usted, y la mayoría no agenda ninguna cita. | Hay chatbots más baratos. En esos el montaje lo hace usted, y la mayoría no agenda citas. | naturalidad |
| Cancelación mensual; se cancela por correo, sin preaviso. | Puede cancelar cada mes con un correo, sin preaviso. | corte: "cancelar" dos veces |
| Garantía de satisfacción de 30 días. ¿No le convence? Le devolvemos el dinero. | Garantía de satisfacción de 30 días. Si no le convence, le devolvemos el dinero. | AI tell: pregunta retórica |
| Descuento por pago por adelantado | Descuento por pago anticipado | corte: "por ... por" |
| ¿Listo para empezar? | Empiece hoy. | AI tell: "¿Listo para...?" (y en masculino); igual que el botón "Empiece hoy" de /es/ |
| ¿Prefiere ver antes cómo funciona? Pruebe la demo, directamente en su navegador. | Si prefiere ver antes cómo funciona, pruebe la demo en su navegador. | AI tell: pregunta retórica; corte "directamente" |
| >Empezar con Chat | >Empiece con Chat | coherencia: imperativo de usted |
| >Empezar con Compleet | >Empiece con Compleet | coherencia: imperativo de usted |

### src/pages/es/demo.astro

| old | new | why |
|---|---|---|
| [meta description] Pruebe la recepcionista digital de Klantkraan en su navegador. Haga una pregunta o pida una cita. ¿Prefiere una demo personalizada con sus servicios? | [meta description] Pruebe la recepcionista digital de Klantkraan en su navegador: haga una pregunta o pida una cita. O solicite una demo personalizada por WhatsApp o correo. | AI tell: pregunta sin respuesta al final de la descripción |
| Una recepcionista de ejemplo, real y en vivo, aquí mismo en su navegador. Haga una pregunta o pida una cita. Sin compromiso. | Una recepcionista de ejemplo que funciona en vivo en su navegador. Haga una pregunta o pida una cita. | corte: "real y en vivo, aquí mismo"; "Sin compromiso" no aplica a una demo gratuita |
| Chatee como un cliente: haga una pregunta o pida una cita. Se abre a pantalla completa. | Escriba como si fuera un cliente. Se abre a pantalla completa. | corte: repite la línea de arriba en móvil; anglicismo "chatee" |
| La recepcionista responde preguntas sobre sus servicios, tarifas y zona de cobertura. En lenguaje natural, las 24 horas del día, y solo con la información que usted mismo configura. | La recepcionista responde preguntas sobre sus servicios, tarifas y zona de cobertura en lenguaje natural, de día y de noche, y solo con la información que usted configura. | gramática (fragmento); coherencia "de día y de noche" |
| ya usan a diario. Quien prefiere | ya usan a diario. Quien prefiera | gramática: subjuntivo |
| Cada cliente y cada solicitud de llamada llega | Cada contacto y cada solicitud de llamada llega | claridad: "lead" es un contacto, no aún un cliente |
| usted. No le soltamos un discurso de venta y no se compromete a nada. | usted. Sin discurso de venta y sin compromiso. | corte |
| > Prefiero el correo | > Envíenos un correo | el botón dice lo que hace |
| La recepcionista es una IA. Comunicarlo es una obligación legal. Lo hacemos en la primera frase de cada conversación, palabra por palabra: | La recepcionista es una IA y la ley obliga a decirlo. Lo hacemos en la primera frase de cada conversación, palabra por palabra: | corte; voz activa |
| ¿Prefiere ver antes los números? | Compare los dos planes. | AI tell: pregunta retórica |
| Eche un vistazo a los dos planes. La demo sigue a un clic de distancia. | Chat y Compleet, ambos con cancelación mensual. | corte: repetía el título; ahora nombra los planes y la condición que el sitio ya indica |

### src/pages/es/rekentool.astro

| old | new | why |
|---|---|---|
| text-(--color-sodium)">€3–75 | text-(--color-sodium)">3–75 € | formato español: euro detrás, como en el resto de /es/ |
| text-(--color-sodium)">±€208 | text-(--color-sodium)">±208 € | formato español: euro detrás |
| "Tiempo de amortización" = los meses | "Tiempo de amortización" son los meses | "=" en prosa |
| Ingresos perdidos al año = llamadas perdidas × valor de cliente × 33% de conversión. Es decir, solo contamos 1 de cada 3 llamadas perdidas como trabajo perdido; sin un sistema de devolución de llamadas, la mayoría de quienes llaman se rinden. | Ingresos perdidos al año = llamadas perdidas × valor por trabajo × 33% de conversión. Solo contamos 1 de cada 3 llamadas perdidas como trabajo perdido, aunque sin un sistema de devolución de llamadas la mayoría de quienes llaman se rinde. | claridad: el razonamiento iba al revés; término igual que el formulario ("valor por trabajo") |
| Plataformas de leads | Portales de presupuestos | anglicismo "leads"; término usual en España para Werkspot y similares |
| ¿Y cuánto cuesta un trabajo a través de Werkspot? | Lo que cuesta un trabajo a través de Werkspot | AI tell: pregunta retórica como título |
| En las plataformas de leads paga por cada lead, y el mismo lead también llega a su competencia. Quien responde primero gana el trabajo; los demás también pagaron. Compárelo con un precio fijo por su propio canal, donde cada llamada simplemente se atiende. | En estos portales paga por cada solicitud, y la misma solicitud llega también a su competencia. Quien responde primero se lleva el trabajo; los demás pagan igual. Compárelo con un precio fijo por su propio canal, donde se atiende cada llamada. | anglicismo "lead"; corte "simplemente" |
| cuesta un solo lead en Werkspot, incluso cuando el trabajo se lo lleva otro. | cuesta una sola solicitud en Werkspot, aunque el trabajo se lo lleve otro. | anglicismo "lead" |
| €0 por lead | 0 € por solicitud | formato español (0 €); anglicismo "lead" |
| Su propio canal además gana valor: cada reseña, cada cliente que repite y cada recomendación es suya, no de la plataforma. | Su propio canal además gana valor: las reseñas, los clientes que repiten y las recomendaciones son suyos, no de la plataforma. | AI tell: tríada "cada..., cada..., cada..." |

### src/pages/es/over.astro

| old | new | why |
|---|---|---|
| Lo que defendemos | Nuestros compromisos | calco de "What we stand for" |
| Los datos de los clientes están en Cloudflare UE + Neon UE + Hetzner FSN1. | Los datos de los clientes se guardan en Cloudflare UE, Neon UE y Hetzner FSN1. | claridad: "+" en prosa |
| Sin permanencia ni contrato anual por defecto. Se queda porque funciona, no porque tenga que hacerlo. | Sin permanencia ni contrato anual por defecto. | AI tell: eslogan "porque X, no porque Y" sin dato |
| BV. Sin inversores externos, sin presión de fondos de capital riesgo y sin cifras de crecimiento por delante de la calidad del cliente. | BV. Sin inversores externos ni presión para anteponer el crecimiento a la calidad. | AI tell: tríada "sin..., sin..., sin..."; los inversores ya salen en la cabecera |
| El desarrollo es deliberadamente en solitario: | El desarrollo es en solitario a propósito: | naturalidad |
| oficios: fontaneros, techadores, electricistas | oficios: fontaneros, tejadores, electricistas | terminología: "tejador" (España) |
| Klantkraan nació de una observación sencilla: según estimaciones del sector, el fontanero, techador o instalador medio pierde alrededor del 28% de sus llamadas. No por falta de ganas. Está en el tejado, en la escalera o con otro cliente. Y aproximadamente 1 de cada 3 de esas llamadas perdidas se habría convertido en un trabajo pagado, de unos 450 € de media, que ahora se lleva la competencia. | Klantkraan nació de una cifra: según estimaciones del sector, el fontanero, tejador o instalador medio pierde alrededor del 28% de sus llamadas. No por falta de ganas: está en el tejado, en la escalera o con otro cliente. Aproximadamente 1 de cada 3 de esas llamadas se habría convertido en un trabajo pagado, de unos 450 € de media, que ahora se lleva la competencia. | claridad; terminología ("tejador") |
| Las soluciones que existían no acababan de encajar. Demasiado caras (899 € de instalación + 199 €/mes), contratos de doce meses, o alguno de esos paquetes americanos que no contempla gastos de desplazamiento ni sabe qué es una tarifa de urgencia. Queríamos crear algo que sonara como parte del propio negocio: con un español fluido, que supiera qué es un calentador, y educado pero directo. | Las opciones que existían no encajaban. Eran demasiado caras (899 € de instalación más 199 € al mes), exigían contratos de doce meses o eran paquetes americanos que no saben qué son los gastos de desplazamiento ni una tarifa de urgencia. Queríamos algo que sonara como parte del propio negocio: con un español fluido, que supiera qué es un calentador, y educado pero directo. | gramática: la enumeración no tenía verbo; corte |
| Klantkraan es justo eso: una recepcionista digital por chat web y WhatsApp que responde preguntas, agenda citas y capta clientes, con un agente telefónico con IA en su propio número como complemento. Instalación llave en mano, cancelación mensual. Creada por alguien que dirige su propia empresa de TI y alojada en Europa. | Klantkraan es eso: una recepcionista digital por chat web y WhatsApp que responde preguntas, agenda citas y capta clientes, más un agente telefónico con IA en su propio número en el plan Compleet. Instalación llave en mano, cancelación mensual. | corte: la última frase repite la cabecera (y decía "Europa" frente a "Países Bajos"); el agente telefónico es del plan Compleet, como dice /es/prijzen/ |
| ¿Preguntas que no necesitan una demo? Escríbanos por WhatsApp o correo. Normalmente | Para preguntas que no necesitan una demo, escríbanos por WhatsApp o correo. Normalmente | AI tell: pregunta retórica |

### src/pages/es/voor-wie.astro

| old | new | why |
|---|---|---|
| Klantkraan funciona para fontaneros, techadores, pintores | Klantkraan funciona para fontaneros, tejadores, pintores | terminología: "tejador" en España (las páginas usan móvil, fontanero, IVA); igual que en /es/aanmelden/ |
| Klantkraan habla el idioma de su oficio. Clases de prueba y cuotas para el gimnasio. Gastos de desplazamiento y tarifas de urgencia para el fontanero. Precios por metro cuadrado y muestras de color para el pintor. | Klantkraan habla el idioma de su oficio: gastos de desplazamiento y tarifas de urgencia para un fontanero, clases de prueba y cuotas para un gimnasio. | AI tell: fragmentos en tríada forzada |
| Ver la solución para {b.labelPluralEs.toLowerCase() | Ver cómo funciona para {b.labelPluralEs.toLowerCase() | claridad: "solución" es jerga comercial |
| Klantkraan funciona para cualquier negocio que reciba preguntas y citas de clientes, desde carpinteros, jardineros y cristaleros hasta peluquerías, fisioterapeutas y autoescuelas. En una breve toma de datos recogemos sus servicios, tarifas y normas internas. A partir de ahí la recepcionista responde como lo haría usted mismo. | Klantkraan funciona para cualquier negocio que reciba preguntas y citas de clientes, desde carpinteros y cristaleros hasta peluquerías y autoescuelas. En una breve entrevista inicial anotamos sus servicios, tarifas y normas internas. A partir de ahí la recepcionista responde como lo haría usted. | corte; "toma de datos" suena a formulario |

### src/pages/es/bedankt.astro

| old | new | why |
|---|---|---|
| Montamos y conectamos su recepcionista. Todo lo hacemos nosotros; usted solo aporta el conocimiento. | Montamos y conectamos su recepcionista. Usted solo aporta la información. | corte: "Todo lo hacemos nosotros" repite "Montamos" |
| Usted lo prueba, da el visto bueno y entra en funcionamiento en su web y WhatsApp. | Usted la prueba, da el visto bueno y se pone en marcha en su web y WhatsApp. | gramática: "la" (la recepcionista); más natural |
| Cancelación mensual; se cancela por correo, sin preaviso. | Puede cancelar cada mes con un correo, sin preaviso. | corte: "cancelar" dos veces |
| No pasa nada: su enlace de pago sigue siendo válido y puede intentarlo más tarde. Si no | Su enlace de pago sigue siendo válido y puede intentarlo más tarde. Si no | corte: muletilla inicial |
| y lo resolvemos juntos. | y lo resolvemos. | corte: "juntos" |

## Flagged, not changed (or changed and needs the founder's OK)

1. **/en/bedankt/ and /es/bedankt/ show a Dutch header and footer.** Their `<Base>` gets no `lang` prop, so it falls back to `nl`. Fix (code, for the main session): add `lang="en"` / `lang="es"` to `<Base>` in both files.
2. **/es/voor-wie/ cards link to the English trade pages** (`href={`/en/${b.slug}/`}`); there are no Spanish trade pages. Either accept it or label the links as English.
3. **Hosting facts contradict each other.** /en/over/ and /es/over/ (and the NL /over/) say "Hosted in the Netherlands" while listing Hetzner FSN1, which is Falkenstein, Germany. The FAQ on every trade page says "Hetzner Frankfurt". The footer says "EU-hosted · Hetzner FSN1". Suggest "Hosted in the EU" and one datacentre name everywhere. Not changed: it is a fact for the founder to confirm.
4. **CHANGED, needs OK: /en/aanmelden/ and /es/aanmelden/.** "Signing up commits you to nothing. We get in touch first to talk everything through." sat under a "Sign up and pay" button; both plans go straight to Mollie checkout. Replaced with the cancel terms the site already states ("Cancel monthly by email, with no notice period. First month 50% off."). The NL /aanmelden/ still says "Aanmelden verplicht u tot niets. Wij nemen eerst contact op ..."; the NL owner should align.
5. **CHANGED, needs OK: /en/dakdekkers/ storm scenario** said "Monday: three review requests sent". Review requests are listed under "What we are building, not available yet" on /en/. Cut to "Monday: three customers helped, zero missed jobs." Check the NL /dakdekkers/ scenario for the same line.
6. **/en/dakdekkers/ contradicts itself on the phone.** The scenario has "Three customers call ... The AI takes all three in parallel" (phone answering, which is the Compleet plan), while the FAQ on the same page says "The receptionist runs on your website and WhatsApp, separate from your phone line." Needs a decision: tie the scenario to Compleet or rewrite it as chat and WhatsApp.
7. **CHANGED: trade-page closing sections promised a trade-specific demo** ("live demo of a gym receptionist", "how it quotes your short-circuit emergency rate", "per-m² vs colour-sample", "how that lands in your WhatsApp"). /en/demo/ embeds one example air-conditioning business (Illa Air Conditioning). Rewritten to say the demo runs on an example business, the same words /en/demo/ uses. If trade-specific EN demos ship, these lines can name them again.
8. **CHANGED: 100% promises removed.** "Missed calls no longer exist." (/en/prijzen/, /es/prijzen/: the plan handles up to 5 calls at once) and "No more missed enquiries." (/en/aannemer/). Still present, not changed: /en/over/ hero "so Dutch business owners never miss a customer enquiry again" and /es/over/ "para que ningún empresario vuelva a perder la consulta de un cliente" (the NL source says the same). The voice guide forbids promising 100%; suggest "miss fewer customer enquiries" / "pierda menos consultas".
9. **Language and number claims differ.** /en/prijzen/ says Chat answers "in Dutch"; the EN trade pages say "in natural English". /es/prijzen/ dropped the "Dutch" in "AI phone agent on your own Dutch number" ("en su propio número"); if the phone agent only works on Dutch numbers, the ES table and blurb need "número neerlandés". /es/over/ tells the founding story with "un español fluido" where EN says "fluent Dutch". Founder to confirm which languages and numbers are sold.
10. **Setup fee** "from €249 (waived for pilot customers)" appears only on /en/prijzen/ and /es/prijzen/. /en/ step 1 and /en/aanmelden/ list "first month €149.50, then €299" with no setup fee. Confirm which is true.
11. **/en/air-conditioning/**: "€450 average value of a missed enquiry. One saved install pays for months." and "One extra install ... covers the subscription for months." At €450 that is 1.5 months of Chat. True only if an install is worth more than the average enquiry; no source given.
12. **/en/rekentool/ button "Have us check it live on your numbers"** (ES "Lo comprobamos en directo con sus cifras") links to /en/demo/, a self-serve chat demo. Suggest "Get a personal demo", or point it at WhatsApp.
13. **Calculator framing.** /en/rekentool/ counts missed calls and says "your own channel, where every caller gets an answer", but the Chat plan answers chat and WhatsApp, not calls. Positioning question for the founder.
14. **Repetition the markup forces.** On every trade page the line "Cancel monthly · Done-for-you setup · 50% off the first month" under the hero repeats the RiskReversal band two blocks lower. Suggest dropping that `<p>` (a markup change).
15. **/en/prijzen/ "VAT rate 21% (reverse-charged for customers outside the Netherlands)"** sits in the "Discount for paying up front" list. Reverse charge covers EU business customers; outside the EU there is no Dutch VAT at all. For the accountant to word; it also belongs with the hero's VAT line.
16. **/en/sportscholen/**: "One extra member a month and you break even" (a €40/month member against €299/month) holds only over a full year of membership. Existing claim; left as is.
17. **/en/demo/ "What you see in the demo"** lists "Lead notification on your phone", which the demo cannot show. Minor.
18. **Dashes kept on purpose:** "4–6 weeks" (/en/dakdekkers/, a range; `test-redesign.mjs` checks this stat's caption width), "€3–75" / "3–75 €" (/en/ and /es/rekentool/, a price range). The "–" in the two payback cells of the calculator is a no-JS placeholder that `/js/rekentool.js` replaces on load. None of these is a dash used as a pause.
19. **Brand line:** "The light stays on." / "La luz sigue encendida." and "Turn the light on." / "Encienda la luz." read naturally in both languages. No change proposed.

## Terminology proposals

| Term | Proposal | Status |
|---|---|---|
| ES roofer: "techador" (Latin America) vs "tejador" (Spain) | "tejador / tejadores", since the pages target Spain (móvil, fontanero, IVA) and /es/aanmelden/ already said "Tejador" | Applied in /es/over/ and the /es/voor-wie/ meta description. `branches.ts` still says "Techadores" (cards on /es/voor-wie/, ES footer); see For other owners |
| EN installateur: "heating engineers" (page H1), "Installers" (cards, footer), "installation engineers" (/en/over/), "Installer (HVAC)" (sign-up select) | "heating engineers" in copy and labels; keep "Installer (HVAC)" in the select because it also covers air-con | /en/over/ fixed; `branches.ts` labelPluralEn pending |
| ES "Cancelación mensual" (footer, RiskReversal, pages) | Understood, but literal. The Spanish idiom is "Sin permanencia". Suggest "Sin permanencia" for labels and "Puede cancelar cada mes con un correo, sin preaviso." for the explanation | Explanation sentence applied on my pages; labels left until the footer and RiskReversal switch together |
| ES "lead" | "solicitud" (request) or "contacto"; on /es/rekentool/ the Werkspot section now uses "portales de presupuestos" and "solicitud" | Applied on my pages; CursusForm still says "lead" |
| ES "e-mail", "newsletter" | "correo", "boletín" | My pages already used "correo"; CursusForm pending |
| EN "e-mail" | "email" (the rest of the EN site) | CursusForm pending |
| "24/7" | "day and night" / "de día y de noche" (voice guide: concrete, never "24/7" alone) | Applied on my pages; the big "24/7" stat on /en/air-conditioning/ left, its caption explains it |
| ES DPA name | "contrato de tratamiento de datos" (as /es/over/ and the footer) | /es/aanmelden/ fixed (was "acuerdo") |
| ES buttons | usted imperative everywhere: "Empiece con Chat", "Pruebe la demo", "Envíenos un correo" | Applied |
| "Disclosure on by default" | "Disclosure always on", because "by default" implies it can be switched off | Applied on all 8 EN trade pages |

## For other owners

**src/components/CursusForm.astro (copy-home)**
- en.eyebrow: `Free e-mail course` → `Free email course`
- en.pitch: `Four short e-mails over nine days, written for tradespeople with a full schedule. ` → `Four short emails over nine days, written for tradespeople with a full schedule. `
- en.emailLabel: `E-mail` → `Email`
- en.error: `Something went wrong. Check your e-mail address and try again.` → `Something went wrong. Check your email address and try again.`
- es.eyebrow: `Curso gratuito por e-mail` → `Curso gratuito por correo`
- es.pitch: `Cuatro e-mails breves en nueve días, escritos para profesionales con la agenda llena. ` → `Cuatro correos breves en nueve días, escritos para profesionales con la agenda llena. `
- es.pitch: `'Prácticos, sin discursos de venta, y todo se puede aplicar por su cuenta. Las lecciones ' +` → `'Prácticos, sin discursos de venta, y todo lo puede aplicar usted mismo. Las lecciones ' +`
- es.lessons[1]: `Lección 2: lo que cuesta un lead cuando lo recompra.` → `Lección 2: lo que cuesta un contacto cuando tiene que comprarlo.`
- es.emailLabel: `E-mail` → `Correo electrónico`
- es.error: `Algo ha fallado. Revise su dirección de e-mail e inténtelo de nuevo.` → `Algo ha fallado. Revise su dirección de correo e inténtelo de nuevo.`
- es.footnote: `La lección 1 llega directamente a su bandeja de entrada. Sin newsletter, sin spam.` → `La lección 1 llega directamente a su bandeja de entrada. Sin boletines ni spam.`

**src/components/RiskReversal.astro (copy-home)**
- en[0].body: `Klantkraan Chat from €149.50 in month one. If it does not work for you, cancel without having to explain.` → `Klantkraan Chat from €149.50 in month one, excl. VAT. If it does not work for you, cancel without having to explain.` (the NL version carries "excl. btw")
- en[2].title: `Live without the hassle` → `We install it` (as NL "Wij installeren het")
- en[2].body: `One small script on your website and the receptionist is running. We install it. You do nothing.` → `One small script on your website and the receptionist is running. You don't have to do anything.`
- es[0].body: `Klantkraan Chat desde 149,50 € el primer mes. Si no le funciona, cancele sin dar explicaciones.` → `Klantkraan Chat desde 149,50 € el primer mes, IVA no incluido. Si no le funciona, cancele sin dar explicaciones.`
- es[2].title: `En marcha sin complicaciones` → `Lo instalamos nosotros` ("sin complicaciones" is on the AI-tell list)
- es[2].body: `Un pequeño script en su web y la recepcionista funciona. Lo instalamos nosotros. Usted no hace nada.` → `Un pequeño script en su web y la recepcionista funciona. Usted no tiene que hacer nada.`

**src/data/branches.ts (no owner listed; used by /es/voor-wie/, the ES nav and the ES footer)**
- roofers labelPluralEs: `Techadores` → `Tejadores`
- installateur labelPluralEn: `Installers` → `Heating engineers` (matches the /en/installateur/ H1; also changes the EN footer and card link text)
- roofers hubLineEn: `A storm protocol that escalates leaks straight to your phone.` → `A storm protocol that sends leaks straight to your phone.` (optional, matches the /en/dakdekkers/ hero)

**src/pages/en/bedankt.astro and src/pages/es/bedankt.astro (code, main session):** add `lang="en"` / `lang="es"` to `<Base>`. See Flagged 1.

**NL owners:** /aanmelden/ "Aanmelden verplicht u tot niets. Wij nemen eerst contact op om alles door te nemen." contradicts the pay-now form (Flagged 4). /dakdekkers/ scenario: check for "review requests sent" (Flagged 5). /over/ "gehost in Nederland" vs Hetzner FSN1 (Flagged 3).

## Test strings

For every changed string, each sentence fragment of 12 or more characters of the old text was searched with `grep -F` in `scripts/test-*.mjs` (test-hamburger, test-integration, test-magnets, test-redesign, test-voor-wie-nav). Plus targeted greps for: "Disclosure on by default", "Three modules", "Ready to", "Ready for", "Let's get started", "Manos a la obra", "Signing up commits", "Prefer email", "WhatsApp us now", "Our pick", "no longer exist", "Plataformas de leads", "techador", "See the solution", "Ver la solución", "Lo que defendemos", "Empezar con", "Listo para", "you build nothing", "24/7".

Hits: **none**. The only related match is a comment in `test-redesign.mjs:153` ("4–6 weken"), and "4–6 weeks" was not changed. Tests that touch these pages check structure, not copy: `/en/bedankt/`, `/es/bedankt/` and `/en/` have no `[data-offer-cta]` (test-magnets), stat-caption widths on `/en/dakdekkers/` and `/en/sportscholen/` (stat values and captions unchanged), and the `/en/` header (test-redesign).

## Verification done

- `grep` for — – and " - " in all owned files: only the ranges and placeholders in Flagged 18.
- All 24 pages return 200 from http://127.0.0.1:4399. Four trade pages briefly returned 500 after one edit put an apostrophe inside a single-quoted JS string ("there's"); fixed to "there is", and all four came back with 200. The dev log shows no other errors from these files.
- Rendered text re-read at 1440 with FAQs open; no horizontal overflow at 393 or 320 on any of the 24 pages.
- Every new string was confirmed present in its file; the diff against the pre-edit copy has text changes only.
