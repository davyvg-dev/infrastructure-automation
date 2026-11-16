/**
 * The Brevo form "Gratis scan aanvragen" (list #6, confirmation template #10).
 * /scan, /websitecheck, /rekentool and /advertentievideos all post into it with
 * the same field names (EMAIL, SCAN_KLUS, SCAN_PROGRAMMAS, SCAN_BEDRIJF) and tell
 * themselves apart through SCAN_PROGRAMMAS (public/js/bron.js). The CSP in
 * public/_headers lists the sibforms host; a new Brevo form means a new URL here.
 */
export const BREVO_ACTION =
  'https://27efbcf4.sibforms.com/serve/MUIFAHNw_Un10JbKvyldJfQiph0ogKUHmFDSWq1XwZNPtf6iuLAQmowIgmnBXITDxHYUIof5S9hHgGLO-7nPUkxtsqvgRl7e8493av8gXjnceijYfcllQhiK0ts9OebUOJaaxZVgDCmDM6ND0yvhblVY6N9DThq-BeqPfCToX9xQbysgHGO7poxDkxSKwDb3gEjF-yeIVUA-m_DA6g=='
