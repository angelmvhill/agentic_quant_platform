"use client";

import { Card, Empty, Table } from "antd";

import { useApiQuery } from "@/lib/api/hooks";

export function CatalogLineageTab({ namespace, name }: { namespace: string; name: string }) {
  const lineage = useApiQuery<Array<Record<string, unknown>>>({
    queryKey: ["dataset", namespace, name, "lineage"],
    path: `/datasets/${encodeURIComponent(namespace)}/${encodeURIComponent(name)}/lineage`,
    select: (raw) => (Array.isArray(raw) ? raw : []),
  });
  const rows = lineage.data ?? [];
  return (
    <Card size="small">
      {rows.length === 0 ? (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No lineage rows." />
      ) : (
        <Table
          size="small"
          rowKey={(row, index) => String(row.id ?? row.version_id ?? index)}
          dataSource={rows}
          columns={Object.keys(rows[0] ?? {}).map((key) => ({ title: key, dataIndex: key }))}
        />
      )}
    </Card>
  );
}
