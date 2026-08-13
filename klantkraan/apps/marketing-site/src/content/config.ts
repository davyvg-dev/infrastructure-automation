// context7: Astro Content Collections via /llmstxt/astro_build_llms-full_txt (2026-05-20)
// Modern (Astro 5+) pattern: defineCollection({ loader: glob({...}), schema: z.object({...}) })
import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'
import { branches } from '../data/branches'

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(160),
    pubDate: z.coerce.date(),
    author: z.string().default('Klantkraan'),
    vertical: z.enum(['loodgieter', 'dakdekker', 'elektricien', 'installateur', 'aannemer', 'schilder', 'algemeen']),
    keywords: z.array(z.string()).default([]),
  }),
})

const gidsen = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/gidsen' }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(200),
    pubDate: z.coerce.date(),
    vertical: z.enum(['loodgieter', 'dakdekker', 'elektricien', 'installateur', 'aannemer', 'schilder']),
    keywords: z.array(z.string()).default([]),
    readingTime: z.number().int().positive(),
  }),
})

// Vertical pSEO pages (TODO §M): vertical × probleem/vergelijking/hub, NEVER
// city×service. Verticals = the 7 branch slugs so cornerstone links can't
// drift, plus 'vakmensen' for the cross-vertical comparison/hub pages
// (breadcrumb parent /voor-wie/).
const branchSlugs = ['vakmensen', ...branches.map((b) => b.slug)] as [string, ...string[]]

const pseo = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pseo' }),
  schema: z.object({
    title: z.string().max(60),
    description: z.string().max(155),
    vertical: z.enum(branchSlugs),
    type: z.enum(['probleem', 'vergelijking', 'hub']),
    targetKeyword: z.string(),
    // Every page needs an unfakeable data layer: sourced stats only (stats
    // policy, research/first-client-market-research-2026-08-10.md §1).
    stats: z
      .array(
        z.object({
          claim: z.string(),
          bron: z.string(),
          bronUrl: z.string().url().optional(),
        }),
      )
      .min(1),
    faq: z.array(z.object({ q: z.string(), a: z.string() })).min(2),
    laatstBijgewerkt: z.coerce.date(),
    /** Slugs of related pseo pages (hub-and-spoke links). */
    related: z.array(z.string()).default([]),
  }),
})

export const collections = { blog, gidsen, pseo }
