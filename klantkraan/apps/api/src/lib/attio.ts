/**
 * Attio API client (typed stub).
 *
 * Real implementation lands in packages/attio after the pnpm workspace
 * scaffold. Until then these wrappers issue typed HTTP requests directly so
 * that route handlers can be wired end-to-end during local dev.
 *
 * Docs: https://docs.attio.com/  (REST, Bearer token)
 */

const ATTIO_BASE = "https://api.attio.com/v2";

export interface AttioPersonInput {
  name: string;
  email_addresses: string[];
  phone_numbers?: string[];
  company?: string;
  kvk_number?: string;
}

export interface AttioPerson {
  id: string;
}

export interface AttioActivityInput {
  recordId: string;
  type: "note" | "call" | "sms" | "email" | "booking";
  content: string;
  metadata?: Record<string, unknown>;
}

async function attioFetch(
  apiKey: string,
  path: string,
  init: RequestInit & { body?: string } = {},
): Promise<unknown> {
  const res = await fetch(`${ATTIO_BASE}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`attio ${path} ${res.status}: ${text.slice(0, 500)}`);
  }
  return res.json();
}

// stub: real implementation in packages/attio after pnpm scaffold lands
export async function findByEmail(apiKey: string, email: string): Promise<AttioPerson | null> {
  const result = (await attioFetch(apiKey, `/objects/people/records/query`, {
    method: "POST",
    body: JSON.stringify({ filter: { email_addresses: { value: email } }, limit: 1 }),
  })) as { data?: Array<{ id: { record_id: string } }> };
  const first = result.data?.[0];
  return first ? { id: first.id.record_id } : null;
}

// stub: real implementation in packages/attio after pnpm scaffold lands
export async function createPerson(
  apiKey: string,
  input: AttioPersonInput,
): Promise<AttioPerson> {
  const body = {
    data: {
      values: {
        name: input.name,
        email_addresses: input.email_addresses,
        phone_numbers: input.phone_numbers ?? [],
        company: input.company,
        kvk_number: input.kvk_number,
      },
    },
  };
  const result = (await attioFetch(apiKey, `/objects/people/records`, {
    method: "POST",
    body: JSON.stringify(body),
  })) as { data: { id: { record_id: string } } };
  return { id: result.data.id.record_id };
}

// stub: real implementation in packages/attio after pnpm scaffold lands
export async function addActivity(
  apiKey: string,
  input: AttioActivityInput,
): Promise<{ id: string }> {
  const body = {
    data: {
      parent_record_id: input.recordId,
      parent_object: "people",
      content_plaintext: input.content,
      metadata: input.metadata ?? {},
    },
  };
  const result = (await attioFetch(apiKey, `/notes`, {
    method: "POST",
    body: JSON.stringify(body),
  })) as { data: { id: { note_id: string } } };
  return { id: result.data.id.note_id };
}
