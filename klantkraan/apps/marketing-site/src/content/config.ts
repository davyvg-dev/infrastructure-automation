// context7: Astro Content Collections via /llmstxt/astro_build_llms-full_txt (2026-05-20)
// Modern (Astro 5+) pattern: defineCollection({ loader: glob({...}), schema: z.object({...}) })
import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'

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

export const collections = { blog, gidsen }
