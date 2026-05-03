"use client";

import { Card, Empty, Table } from "antd";

import { useApiQuery } from "@/lib/api/hooks";

export function CatalogEntitiesTab({ iceberg_identifier }: { iceberg_identifier: string }) {
  const entities = useApiQuery<Array<Record<string, unknown>>>({
    queryKey: ["dataset", iceberg_identifier, "entities"],
    path: "/entities/dataset",
    query: { iceberg_identifier },
    select: (raw) => (Array.isArray(raw) ? raw : []),
  });
  const rows = entities.data ?? [];
  return (
    <Card size="small">
      {rows.length === 0 ? (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No entity mappings." />
      ) : (
        <Table
          size="small"
          rowKey={(row, index) => String(row.id ?? row.entity_id ?? index)}
          dataSource={rows}
          columns={Object.keys(rows[0] ?? {}).map((key) => ({ title: key, dataIndex: key }))}
        />
      )}
    </Card>
  );
}
