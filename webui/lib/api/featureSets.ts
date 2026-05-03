"use client";

import { useApiQuery } from "./hooks";

export interface FeatureSetSummary {
  id: string;
  name: string;
  kind: string;
  version: number;
  status?: string;
  specs: string[];
  description?: string | null;
  tags?: string[];
  default_lookback_days?: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface FeatureSetPreviewResp {
  columns: string[];
  rows: Array<Record<string, unknown>>;
  warning?: string;
  data?: Array<Record<string, unknown>>;
  [key: string]: unknown;
}

export function useFeatureSets() {
  return useApiQuery<FeatureSetSummary[]>({
    queryKey: ["feature-sets"],
    path: "/feature-sets/",
    select: (raw) => (Array.isArray(raw) ? raw : []),
  });
}

export function useFeatureSet(id: string | null | undefined) {
  return useApiQuery<FeatureSetSummary>({
    queryKey: ["feature-set", id ?? ""],
    path: id ? `/feature-sets/${encodeURIComponent(id)}` : "/feature-sets/",
    enabled: Boolean(id),
  });
}

export function useFeatureSetVersions(id: string | null | undefined) {
  return useApiQuery<Array<Record<string, unknown>>>({
    queryKey: ["feature-set", id ?? "", "versions"],
    path: id ? `/feature-sets/${encodeURIComponent(id)}/versions` : "/feature-sets/",
    enabled: Boolean(id),
    select: (raw) => (Array.isArray(raw) ? raw : []),
  });
}

export function useFeatureSetUsages(id: string | null | undefined) {
  return useApiQuery<Array<Record<string, unknown>>>({
    queryKey: ["feature-set", id ?? "", "usages"],
    path: id ? `/feature-sets/${encodeURIComponent(id)}/usages` : "/feature-sets/",
    enabled: Boolean(id),
    select: (raw) => (Array.isArray(raw) ? raw : []),
  });
}
