import { apiFetch } from "./client";

export interface RagCorpusInfo {
  name: string;
  level?: string;
  order?: "first" | "second" | "third" | string;
  description?: string;
  chunks: number;
}

export interface RagHierarchy {
  categories: Record<string, Record<string, string[]>>;
}

export interface RagHit {
  doc_id: string;
  corpus: string;
  level: string;
  score: number;
  text: string;
  vt_symbol?: string | null;
  as_of?: string | null;
  metadata?: Record<string, unknown>;
}

export interface TaskAccepted {
  task_id: string;
  stream_url?: string;
  status?: string;
}

function hits(payload: unknown): RagHit[] {
  if (Array.isArray(payload)) return payload as RagHit[];
  if (payload && typeof payload === "object") {
    const value = (payload as Record<string, unknown>).hits;
    if (Array.isArray(value)) return value as RagHit[];
  }
  return [];
}

export const RagApi = {
  async corpora(): Promise<RagCorpusInfo[]> {
    const payload = await apiFetch<unknown>("/rag/corpora");
    if (Array.isArray(payload)) return payload as RagCorpusInfo[];
    const corpora = (payload as Record<string, unknown>)?.corpora;
    return Array.isArray(corpora) ? (corpora as RagCorpusInfo[]) : [];
  },
  hierarchy(): Promise<RagHierarchy> {
    return apiFetch<RagHierarchy>("/rag/hierarchy");
  },
  async query(payload: Record<string, unknown>): Promise<RagHit[]> {
    return hits(await apiFetch("/rag/query", { method: "POST", body: payload }));
  },
  async walk(payload: Record<string, unknown>): Promise<RagHit[]> {
    return hits(await apiFetch("/rag/walk", { method: "POST", body: payload }));
  },
  indexCorpus(corpus: string): Promise<TaskAccepted> {
    return apiFetch<TaskAccepted>(`/rag/index/${encodeURIComponent(corpus)}`, { method: "POST" });
  },
  raptor(corpus: string): Promise<TaskAccepted> {
    return apiFetch<TaskAccepted>(`/rag/raptor/${encodeURIComponent(corpus)}`, { method: "POST" });
  },
  refreshL0(): Promise<TaskAccepted> {
    return apiFetch<TaskAccepted>("/rag/refresh-l0", { method: "POST" });
  },
  refreshHierarchy(): Promise<TaskAccepted> {
    return apiFetch<TaskAccepted>("/rag/refresh-hierarchy", { method: "POST" });
  },
};
