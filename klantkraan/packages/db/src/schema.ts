/**
 * Drizzle schema — mirrors `@kk/domain` interfaces 1:1.
 *
 * Field names in TypeScript stay camelCase (matching the domain types);
 * Postgres column names are snake_case for SQL idiomatic-ness. Inferred
 * `*Row` types are re-exported from `index.ts`.
 */

import { sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  check,
  date,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  smallint,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";

// ---------------------------------------------------------------------------
// Enums — exact unions from @kk/domain.
// ---------------------------------------------------------------------------

export const verticalEnum = pgEnum("vertical", ["loodgieter", "dakdekker"]);

export const tierEnum = pgEnum("tier", ["lite", "pro", "max"]);

export const clientStatusEnum = pgEnum("client_status", [
  "lead",
  "signed",
  "onboarding",
  "live",
  "paused",
  "churned",
]);

export const callOutcomeEnum = pgEnum("call_outcome", [
  "answered_by_ai",
  "transferred_to_human",
  "callback_scheduled",
  "emergency_transferred",
  "voicemail",
  "abandoned",
]);

export const bookingSourceEnum = pgEnum("booking_source", [
  "ai",
  "cal_com",
  "manual",
]);

export const reviewChannelEnum = pgEnum("review_channel", ["sms", "email"]);

export const reviewStatusEnum = pgEnum("review_status", [
  "requested",
  "opened",
  "submitted",
  "declined",
  "expired",
]);

export const suppressionReasonEnum = pgEnum("suppression_reason", [
  "stop_keyword",
  "unsubscribe_link",
  "hard_bounce",
  "complaint",
  "manual",
]);

// ---------------------------------------------------------------------------
// clients — the tenant table. One row per signed Klantkraan customer.
// ---------------------------------------------------------------------------

export const clients = pgTable(
  "clients",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    slug: text("slug").notNull(),
    name: text("name").notNull(),
    kvkNumber: text("kvk_number").notNull(),
    vertical: verticalEnum("vertical").notNull(),
    tier: tierEnum("tier").notNull(),
    status: clientStatusEnum("status").notNull(),
    e164Primary: text("e164_primary").notNull(),
    escalationE164: text("escalation_e164").notNull(),
    voorrijkostenCents: integer("voorrijkosten_cents").notNull(),
    spoedtoeslagCents: integer("spoedtoeslag_cents").notNull(),
    materiaalopslagBps: integer("materiaalopslag_bps").notNull(),
    agentId: text("agent_id"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    signedAt: timestamp("signed_at", { withTimezone: true }),
    liveAt: timestamp("live_at", { withTimezone: true }),
  },
  (table) => [uniqueIndex("clients_slug_uniq").on(table.slug)],
);

// ---------------------------------------------------------------------------
// calls — every Synthflow-handled call, one row per session.
// ---------------------------------------------------------------------------

export const calls = pgTable(
  "calls",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id")
      .notNull()
      .references(() => clients.id, { onDelete: "cascade" }),
    fromE164: text("from_e164").notNull(),
    toE164: text("to_e164").notNull(),
    startedAt: timestamp("started_at", { withTimezone: true }).notNull(),
    endedAt: timestamp("ended_at", { withTimezone: true }).notNull(),
    durationSeconds: integer("duration_seconds").notNull(),
    outcome: callOutcomeEnum("outcome").notNull(),
    promptHash: text("prompt_hash").notNull(),
    aiDisclosurePlayed: boolean("ai_disclosure_played").notNull(),
    transcriptUrl: text("transcript_url"),
    recordingUrl: text("recording_url"),
    intent: text("intent"),
    scheduledCallbackAt: timestamp("scheduled_callback_at", {
      withTimezone: true,
    }),
  },
  (table) => [
    index("calls_client_id_idx").on(table.clientId),
    index("calls_started_at_idx").on(table.startedAt),
  ],
);

// ---------------------------------------------------------------------------
// bookings — appointment scheduled via AI, Cal.com, or manual entry.
// ---------------------------------------------------------------------------

export const bookings = pgTable(
  "bookings",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id")
      .notNull()
      .references(() => clients.id, { onDelete: "cascade" }),
    callId: uuid("call_id").references(() => calls.id, { onDelete: "set null" }),
    customerE164: text("customer_e164").notNull(),
    customerName: text("customer_name").notNull(),
    scheduledAt: timestamp("scheduled_at", { withTimezone: true }).notNull(),
    durationMinutes: integer("duration_minutes").notNull(),
    source: bookingSourceEnum("source").notNull(),
    notes: text("notes"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("bookings_client_id_idx").on(table.clientId),
    index("bookings_call_id_idx").on(table.callId),
    index("bookings_scheduled_at_idx").on(table.scheduledAt),
  ],
);

// ---------------------------------------------------------------------------
// reviews — Google review requests sent via SMS or email after a job.
// ---------------------------------------------------------------------------

export const reviews = pgTable(
  "reviews",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id")
      .notNull()
      .references(() => clients.id, { onDelete: "cascade" }),
    bookingId: uuid("booking_id").references(() => bookings.id, {
      onDelete: "set null",
    }),
    customerE164: text("customer_e164").notNull(),
    channel: reviewChannelEnum("channel").notNull(),
    status: reviewStatusEnum("status").notNull(),
    requestedAt: timestamp("requested_at", { withTimezone: true }).notNull(),
    submittedAt: timestamp("submitted_at", { withTimezone: true }),
    googleReviewId: text("google_review_id"),
    rating: smallint("rating"),
  },
  (table) => [
    index("reviews_client_id_idx").on(table.clientId),
    index("reviews_booking_id_idx").on(table.bookingId),
  ],
);

// ---------------------------------------------------------------------------
// suppression_list — opted-out / bounced contacts. At least one of the two
// hash columns must be non-null (enforced by CHECK).
// ---------------------------------------------------------------------------

export const suppressionList = pgTable(
  "suppression_list",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    e164Hash: text("e164_hash"),
    emailHash: text("email_hash"),
    reason: suppressionReasonEnum("reason").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("suppression_e164_hash_idx").on(table.e164Hash),
    index("suppression_email_hash_idx").on(table.emailHash),
    check(
      "suppression_at_least_one_hash",
      sql`${table.e164Hash} IS NOT NULL OR ${table.emailHash} IS NOT NULL`,
    ),
  ],
);

// ---------------------------------------------------------------------------
// mrr_snapshots — monthly business-state snapshot, written by the finance job.
// snapshot_date is the natural PK (one row per month).
// ---------------------------------------------------------------------------

export const mrrSnapshots = pgTable("mrr_snapshots", {
  snapshotDate: date("snapshot_date").primaryKey(),
  totalCents: bigint("total_cents", { mode: "number" }).notNull(),
  activeClients: integer("active_clients").notNull(),
  newThisMonth: integer("new_this_month").notNull(),
  churnedThisMonth: integer("churned_this_month").notNull(),
});

// ---------------------------------------------------------------------------
// events — generic audit log. `payload` is a free-form jsonb so new event
// types do not require a migration; readers must validate via zod at the edge.
// ---------------------------------------------------------------------------

export const events = pgTable(
  "events",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    ts: timestamp("ts", { withTimezone: true }).notNull().defaultNow(),
    type: text("type").notNull(),
    clientId: uuid("client_id").references(() => clients.id, {
      onDelete: "set null",
    }),
    payload: jsonb("payload").notNull().default(sql`'{}'::jsonb`),
  },
  (table) => [
    index("events_client_id_idx").on(table.clientId),
    index("events_ts_idx").on(table.ts),
    index("events_type_idx").on(table.type),
  ],
);

// ---------------------------------------------------------------------------
// Inferred row types — one Select + one Insert per table. Naming mirrors
// the domain interfaces (`ClientRow` ≈ `Client`).
// ---------------------------------------------------------------------------

export type ClientRow = typeof clients.$inferSelect;
export type ClientInsert = typeof clients.$inferInsert;

export type CallRow = typeof calls.$inferSelect;
export type CallInsert = typeof calls.$inferInsert;

export type BookingRow = typeof bookings.$inferSelect;
export type BookingInsert = typeof bookings.$inferInsert;

export type ReviewRow = typeof reviews.$inferSelect;
export type ReviewInsert = typeof reviews.$inferInsert;

export type SuppressionRow = typeof suppressionList.$inferSelect;
export type SuppressionInsert = typeof suppressionList.$inferInsert;

export type MrrSnapshotRow = typeof mrrSnapshots.$inferSelect;
export type MrrSnapshotInsert = typeof mrrSnapshots.$inferInsert;

export type EventRow = typeof events.$inferSelect;
export type EventInsert = typeof events.$inferInsert;
