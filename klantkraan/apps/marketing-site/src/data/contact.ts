/**
 * Single source of truth for founder contact: WhatsApp, phone, email.
 * Swap to a CM.com landline later by editing the three NUMBER consts only.
 *
 * Format rules:
 *   phoneNumberRaw  — international with +, no spaces  → for tel: links
 *   waNumberRaw     — international, no +, no spaces   → for wa.me links
 *   phoneDisplay    — human-readable                   → for visible text
 */

export const contact = {
  phoneNumberRaw: '+31644588321',
  // WhatsApp stays on the old number until WhatsApp is confirmed active on the new one.
  waNumberRaw: '31621645206',
  phoneDisplay: '+31 6 44 58 83 21',
  email: 'hallo@klantkraan.nl',
  emailSubject: 'Klantkraan demo',
  waMessage: 'Hoi, ik zag Klantkraan en wil graag meer weten.',
} as const

export const waLink = `https://wa.me/${contact.waNumberRaw}?text=${encodeURIComponent(contact.waMessage)}`
export const telLink = `tel:${contact.phoneNumberRaw}`
export const mailLink = `mailto:${contact.email}?subject=${encodeURIComponent(contact.emailSubject)}`
