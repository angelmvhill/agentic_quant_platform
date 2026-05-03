import { apiFetch } from "./client";

export interface AirbyteConnector {
  id: string;
  name: string;
  kind: "source" | "destination" | string;
  docker_image?: string;
  version?: string;
  tags: string[];
  streams?: Array<{ name: string }>;
  [key: string]: unknown;
}

export interface AirbyteConnection {
  id: string;
  name?: string;
  source_id?: string;
  destination_id?: string;
  status?: string;
  tags?: string[];
  streams?: Array<{ name: string }>;
  [key: string]: unknown;
}

export interface AirbyteRun {
  id: string;
  connection_id?: string;
  status?: string;
  started_at?: string | null;
  finished_at?: string | null;
  [key: string]: unknown;
}

export interface AirbyteTask {
  task_id: string;
  stream_url?: string;
  status?: string;
}

export const AirbyteApi = {
  discover(connectorId: string, config: Record<string, unknown>): Promise<AirbyteTask> {
    return apiFetch<AirbyteTask>("/airbyte/discover", {
      method: "POST",
      body: { connector_id: connectorId, config, dry_run: true },
    });
  },
  embeddedRead(connectorId: string, config: Record<string, unknown>): Promise<AirbyteTask> {
    return apiFetch<AirbyteTask>("/airbyte/embedded-read", {
      method: "POST",
      body: { connector_id: connectorId, config, dry_run: true },
    });
  },
  sync(connectionId: string): Promise<AirbyteTask> {
    return apiFetch<AirbyteTask>("/airbyte/sync", {
      method: "POST",
      body: { connection_id: connectionId },
    });
  },
};
