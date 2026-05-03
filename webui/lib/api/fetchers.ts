import { apiFetch } from "./client";

export interface FetcherSummary {
  name: string;
  kind?: string;
  description?: string;
  vendor?: string;
  domains?: string[];
  [key: string]: unknown;
}

export interface FetcherProbeResult {
  ok: boolean;
  error?: string;
  message?: string;
  [key: string]: unknown;
}

export const fetchersApi = {
  list(): Promise<FetcherSummary[]> {
    return apiFetch<FetcherSummary[]>("/fetchers");
  },
  probe(name: string, payload: Record<string, unknown>): Promise<FetcherProbeResult> {
    return apiFetch<FetcherProbeResult>("/fetchers/probe", {
      method: "POST",
      body: { name, params: payload },
    });
  },
};
