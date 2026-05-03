"use client";

import { Alert, Button, Card, Descriptions, Space } from "antd";

import { apiFetch } from "@/lib/api/client";
import { useApiQuery } from "@/lib/api/hooks";

export function CatalogDataHubTab({ iceberg_identifier }: { iceberg_identifier: string }) {
  const status = useApiQuery<Record<string, unknown>>({
    queryKey: ["datahub", "dataset", iceberg_identifier],
    path: "/datahub/dataset",
    query: { iceberg_identifier },
    staleTime: 30_000,
  });

  return (
    <Card size="small">
      <Space direction="vertical" style={{ width: "100%" }}>
        {status.error ? <Alert type="warning" showIcon message={status.error.message} /> : null}
        <Descriptions size="small" bordered column={1}>
          <Descriptions.Item label="Iceberg identifier">{iceberg_identifier}</Descriptions.Item>
          <Descriptions.Item label="DataHub URN">
            {String(status.data?.urn ?? "not synced")}
          </Descriptions.Item>
          <Descriptions.Item label="Sync status">
            {String(status.data?.status ?? "unknown")}
          </Descriptions.Item>
        </Descriptions>
        <Button
          onClick={() =>
            apiFetch("/datahub/push", {
              method: "POST",
              body: { iceberg_identifier },
            }).then(() => status.refetch())
          }
        >
          Push metadata
        </Button>
      </Space>
    </Card>
  );
}
