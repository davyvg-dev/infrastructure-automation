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
    vertical: z.enum(['loodgieter', 'dakdekker', 'elektricien', 'installateur', 'aannemer', 'algemeen']),
    keywords: z.array(z.string()).default([]),
  }),
})

export const collections = { blog }
