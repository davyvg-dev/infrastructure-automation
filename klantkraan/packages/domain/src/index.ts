export type Vertical = 'loodgieter' | 'dakdekker'
export type Tier = 'lite' | 'pro' | 'max'
export type ClientStatus = 'lead' | 'signed' | 'onboarding' | 'live' | 'paused' | 'churned'

export interface Client {
  id: string
  slug: string
  name: string
  kvkNumber: string
  vertical: Vertical
  tier: Tier
  status: ClientStatus
  e164Primary: string
  escalationE164: string
  voorrijkostenCents: number
  spoedtoeslagCents: number
  materiaalopslagBps: number
  agentId: string | null
  createdAt: string
  signedAt: string | null
  liveAt: string | null
}

export type CallOutcome =
  | 'answered_by_ai'
  | 'transferred_to_human'
  | 'callback_scheduled'
  | 'emergency_transferred'
  | 'voicemail'
  | 'abandoned'

export interface Call {
  id: string
  clientId: string
  fromE164: string
  toE164: string
  startedAt: string
  endedAt: string
  durationSeconds: number
  outcome: CallOutcome
  promptHash: string
  aiDisclosurePlayed: boolean
  transcriptUrl: string | null
  recordingUrl: string | null
  intent: string | null
  scheduledCallbackAt: string | null
}

export interface Booking {
  id: string
  clientId: string
  callId: string | null
  customerE164: string
  customerName: string
  scheduledAt: string
  durationMinutes: number
  source: 'ai' | 'cal_com' | 'manual'
  notes: string | null
  createdAt: string
}

export type ReviewChannel = 'sms' | 'email'
export type ReviewStatus = 'requested' | 'opened' | 'submitted' | 'declined' | 'expired'

export interface Review {
  id: string
  clientId: string
  bookingId: string | null
  customerE164: string
  channel: ReviewChannel
  status: ReviewStatus
  requestedAt: string
  submittedAt: string | null
  googleReviewId: string | null
  rating: number | null
}

export type SuppressionReason =
  | 'stop_keyword'
  | 'unsubscribe_link'
  | 'hard_bounce'
  | 'complaint'
  | 'manual'

export interface Suppression {
  id: string
  e164Hash: string | null
  emailHash: string | null
  reason: SuppressionReason
  createdAt: string
}

export interface SubscriptionSnapshot {
  clientId: string
  tier: Tier
  monthlyCents: number
  startedAt: string
  cancelledAt: string | null
}
