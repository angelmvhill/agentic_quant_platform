import { apiFetch } from "./client";

export interface AgentSpecSummary {
  name: string;
  role?: string;
  team?: string;
  version?: number;
  description?: string;
  tags?: string[];
}

export interface AgentRunV2Summary {
  id: string;
  spec_name: string;
  status: string;
  spec_version_id?: string | null;
  cost_usd?: number | null;
  n_calls?: number;
  n_tool_calls?: number;
  n_rag_hits?: number;
  started_at?: string | null;
  finished_at?: string | null;
  completed_at?: string | null;
  error?: string | null;
}

export interface AgentRunV2Step {
  id?: string;
  step_index?: number;
  kind?: string;
  name?: string;
  status?: string;
  input?: unknown;
  inputs?: unknown;
  output?: unknown;
  created_at?: string | null;
}

export interface AgentRunV2Detail extends AgentRunV2Summary {
  inputs?: Record<string, unknown>;
  output?: unknown;
  steps: AgentRunV2Step[];
  artifacts?: unknown[];
}

export interface AgentEvaluation {
  id: string;
  spec_name?: string;
  status?: string;
  score?: number | null;
  n_cases: number;
  n_passed: number;
  created_at?: string | null;
  metrics?: Record<string, unknown>;
}

function asArray<T>(payload: unknown, key: string): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === "object") {
    const value = (payload as Record<string, unknown>)[key];
    if (Array.isArray(value)) return value as T[];
    const items = (payload as Record<string, unknown>).items;
    if (Array.isArray(items)) return items as T[];
  }
  return [];
}

export const AgentsApi = {
  async listSpecs(): Promise<AgentSpecSummary[]> {
    return asArray<AgentSpecSummary>(await apiFetch("/agents/specs"), "specs");
  },
  async listRuns(query: Record<string, string | number | boolean | undefined> = {}): Promise<AgentRunV2Summary[]> {
    return asArray<AgentRunV2Summary>(await apiFetch("/agents/runs/v2", { query }), "runs");
  },
  async getRun(id: string): Promise<AgentRunV2Detail> {
    return apiFetch<AgentRunV2Detail>(`/agents/runs/v2/${encodeURIComponent(id)}`);
  },
  async replayRun(id: string): Promise<AgentRunV2Detail> {
    return apiFetch<AgentRunV2Detail>(`/agents/runs/v2/${encodeURIComponent(id)}/replay`, {
      method: "POST",
    });
  },
  async runSpecSync(specName: string, inputs: Record<string, unknown>): Promise<AgentRunV2Detail> {
    return apiFetch<AgentRunV2Detail>("/agents/runs/v2/sync", {
      method: "POST",
      body: { spec_name: specName, inputs },
    });
  },
  async listEvaluations(query: Record<string, string | number | boolean | undefined> = {}): Promise<AgentEvaluation[]> {
    return asArray<AgentEvaluation>(await apiFetch("/agents/evaluations", { query }), "evaluations");
  },
};
