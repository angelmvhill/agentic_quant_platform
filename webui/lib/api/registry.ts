"use client";

import { useApiQuery } from "./hooks";

export interface ParamSchema {
  name: string;
  type?: string;
  annotation?: string;
  default?: unknown;
  required?: boolean;
  description?: string;
  enum?: Array<string | number | boolean>;
}

export interface ComponentSummary {
  alias: string;
  kind?: string;
  qualname?: string;
  module_path?: string;
  tags?: string[];
  params: ParamSchema[];
  description?: string;
  full_doc?: string;
}

export function useRegistryKind(kind: string | null | undefined) {
  return useApiQuery<ComponentSummary[]>({
    queryKey: ["registry", "kind", kind ?? ""],
    path: kind ? `/registry/${encodeURIComponent(kind)}` : "/registry",
    enabled: Boolean(kind),
    select: (raw) => (Array.isArray(raw) ? raw : []),
    staleTime: 60_000,
  });
}

export function useRegistryComponent(kind: string | null | undefined, alias: string | null | undefined) {
  return useApiQuery<ComponentSummary>({
    queryKey: ["registry", "component", kind ?? "", alias ?? ""],
    path:
      kind && alias
        ? `/registry/${encodeURIComponent(kind)}/${encodeURIComponent(alias)}`
        : "/registry",
    enabled: Boolean(kind && alias),
    staleTime: 60_000,
  });
}

export function buildSpec(component: ComponentSummary | undefined, kwargs: Record<string, unknown>) {
  if (!component) return undefined;
  return {
    class: component.alias,
    module_path: component.module_path,
    kwargs,
  };
}
