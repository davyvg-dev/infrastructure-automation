#!/usr/bin/env node
// Facebook-groepen posting scheduler (handmatig plaatsen, geen bot).
// Vertelt wat er deze week aan de beurt is en print de plak-klare tekst.
//
//   node schedule.mjs            wat moet ik deze week plaatsen?
//   node schedule.mjs --week 2   toon een specifieke week
//   node schedule.mjs --all      het hele plan in één overzicht
//   node schedule.mjs --post 003 toon één draft
//
// Pas START_DATE aan naar de maandag waarop je begint.

import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DRAFTS = join(HERE, 'drafts');

const START_DATE = new Date('2026-06-29T00:00:00'); // eerste maandag — pas aan
const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000;

const PLAN = [
  { week: 1, di: { post: '001' }, do: { post: '002' } },
  { week: 2, di: { post: '003' }, do: { post: '004' } },
  { week: 3, di: { post: '005' }, do: { post: '001', note: 'herhaling — andere groep, andere openingszin' } },
  { week: 4, di: { post: '003', note: 'herhaling — andere groep' }, do: { post: '006', note: 'promo — alleen waar toegestaan' } },
];

const RULE_HINT = {
  'value-only': "kies een 'value-only' groep uit groups.md (mag bijna overal)",
  'soft-mention': "alleen in groepen waar een lichte zakelijke insteek mag",
  'promo-allowed': "ALLEEN in promo-toegestane groepen of het promo-draadje",
};

function loadDraft(post) {
  const file = readdirSync(DRAFTS).find((f) => f.startsWith(`fb-${post}-`));
  if (!file) return null;
  const raw = readFileSync(join(DRAFTS, file), 'utf8');
  const fm = raw.match(/^---\n([\s\S]*?)\n---/);
  const rule = fm ? (fm[1].match(/group_rule_type:\s*(\S+)/) || [])[1] : undefined;
  const title = (raw.match(/^#\s+(.+)$/m) || [])[1] || file;
  const body = (raw.match(/## Post body[^\n]*\n([\s\S]*?)(?:\n## |\s*$)/) || [])[1];
  return { file, rule, title, body: (body || '').trim() };
}

function currentWeek() {
  const diff = Math.floor((Date.now() - START_DATE.getTime()) / MS_PER_WEEK);
  return Math.min(Math.max(diff + 1, 1), PLAN.length);
}

function printSlot(dag, slot) {
  const d = loadDraft(slot.post);
  if (!d) {
    console.log(`\n${dag} · fb-${slot.post} · (draft niet gevonden)`);
    return;
  }
  console.log(`\n${'─'.repeat(64)}`);
  console.log(`${dag} · fb-${slot.post} · ${d.rule || '?'}`);
  if (slot.note) console.log(`(${slot.note})`);
  console.log(`→ plaats: ${RULE_HINT[d.rule] || 'check groups.md'}`);
  console.log(`${'─'.repeat(64)}`);
  console.log(d.body);
}

function showWeek(n) {
  const wk = PLAN.find((w) => w.week === n);
  if (!wk) {
    console.log(`Week ${n} bestaat niet (plan heeft ${PLAN.length} weken).`);
    return;
  }
  console.log(`\n=== Week ${wk.week} — wat te plaatsen ===`);
  printSlot('Dinsdag', wk.di);
  printSlot('Donderdag', wk.do);
  console.log(`\nHerinnering: max 1 promo per 4 value-posts. Niet dezelfde tekst dezelfde dag in meerdere groepen.`);
}

function showAll() {
  console.log('\n=== Heel het plan (6 drafts, 4 weken) ===');
  for (const wk of PLAN) {
    const di = loadDraft(wk.di.post);
    const wo = loadDraft(wk.do.post);
    console.log(`Week ${wk.week}:  di fb-${wk.di.post} (${di?.rule || '?'})   |   do fb-${wk.do.post} (${wo?.rule || '?'})`);
  }
  console.log(`\nDetails per week: node schedule.mjs --week <n>`);
}

function showPost(post) {
  printSlot('Draft', { post });
}

const [cmd, val] = process.argv.slice(2);
if (!cmd || cmd === 'now' || cmd === 'week') showWeek(currentWeek());
else if (cmd === '--all' || cmd === 'all' || cmd === 'list') showAll();
else if (cmd === '--week') showWeek(Number(val));
else if (cmd === '--post') showPost(String(val).padStart(3, '0'));
else {
  console.log('Gebruik: node schedule.mjs [ --week <n> | --all | --post <nr> ]');
}
