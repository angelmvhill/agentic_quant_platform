import { apiFetch } from "./client";

export interface DagsterStatus {
  graphql_url?: string | null;
  code_location: string;
  module_path: string;
  grpc_host: string;
  grpc_port: number;
}

export interface DagsterAssetNode {
  assetKey?: { path: string[] };
  key?: string[];
  groupName?: string;
  description?: string | null;
}

export interface DagsterRunSummary {
  runId: string;
  status?: string;
  pipelineName?: string;
  startTime?: number | null;
}

export const dagsterApi = {
  status(): Promise<DagsterStatus> {
    return apiFetch<DagsterStatus>("/dagster/status");
  },
  listAssets(): Promise<{ asset_nodes: DagsterAssetNode[] }> {
    return apiFetch<{ asset_nodes: DagsterAssetNode[] }>("/dagster/assets");
  },
  listRuns(limit = 25): Promise<{ runs: DagsterRunSummary[] }> {
    return apiFetch<{ runs: DagsterRunSummary[] }>("/dagster/runs", { query: { limit } });
  },
  trigger(asset_keys: string[][]): Promise<unknown> {
    return apiFetch("/dagster/materialize", { method: "POST", body: { asset_keys } });
  },
};
