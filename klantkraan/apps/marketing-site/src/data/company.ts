// Single source of truth for company registration details. Every page renders
// from here — updating a number means editing this file only.
export const company = {
  tradeName: 'Klantkraan',
  legalName: 'T4 Software Consulting BV',
  kvk: '90232135',
  // BTW number pending from the founder; pages hide the field while empty.
  btw: '',
} as const;
