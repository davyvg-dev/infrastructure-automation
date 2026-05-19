import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";
import type { Bindings } from "../env.js";
import { addActivity, createPerson, findByEmail } from "../lib/attio.js";
import { isSuppressed } from "../lib/suppression.js";

export const leadRouter = new Hono<{ Bindings: Bindings }>();

const LeadSchema = z.object({
  name: z.string().min(2).max(200),
  email: z.string().email(),
  phone: z
    .string()
    .min(8)
    .max(20)
    .regex(/^\+?[0-9 ()-]+$/)
    .optional(),
  message: z.string().min(1).max(4000),
});

leadRouter.post(
  "/lead",
  zValidator("json", LeadSchema),
  async (c) => {
    const data = c.req.valid("json");

    // Suppression check before any follow-up (06-outbound/gdpr-compliance.md).
    const supp = await isSuppressed(c.env.NEON_DATABASE_URL, {
      email: data.email,
      phone: data.phone,
    });
    if (supp.suppressed) {
      return c.json({ error: "suppressed", reason: supp.reason }, 409);
    }

    // Attio upsert — Person + Note with the raw message.
    let person = await findByEmail(c.env.ATTIO_API_KEY, data.email);
    if (!person) {
      person = await createPerson(c.env.ATTIO_API_KEY, {
        name: data.name,
        email_addresses: [data.email],
        phone_numbers: data.phone ? [data.phone] : [],
      });
    }
    await addActivity(c.env.ATTIO_API_KEY, {
      recordId: person.id,
      type: "note",
      content: `Site lead: ${data.message}`,
    });

    return c.json({ id: person.id }, 201);
  },
);
