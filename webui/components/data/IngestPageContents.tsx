"use client";

import { App, Button, Card, Form, Input, InputNumber, Select, Space, Typography } from "antd";
import { useState } from "react";

import { PageContainer } from "@/components/shell/PageContainer";
import { apiFetch } from "@/lib/api/client";
import { useChatStream } from "@/lib/ws";

const { Paragraph, Text } = Typography;

interface TaskAccepted {
  task_id: string;
  stream_url?: string;
}

export function IngestPageContents() {
  const { message } = App.useApp();
  const [taskId, setTaskId] = useState<string | null>(null);
  const stream = useChatStream(taskId);

  async function submit(values: Record<string, unknown>) {
    try {
      const response = await apiFetch<TaskAccepted>("/pipelines/ingest", {
        method: "POST",
        body: {
          source_dir: values.source_dir,
          format: values.format,
          namespace: values.namespace,
          max_rows: values.max_rows,
          max_files: values.max_files,
          annotate: values.annotate,
        },
      });
      setTaskId(response.task_id);
      message.success(`Ingest queued: ${response.task_id}`);
    } catch (err) {
      message.error((err as Error).message);
    }
  }

  return (
    <PageContainer
      title="Data ingest"
      subtitle="Queue local CSV/Parquet/JSON ingestion into the Iceberg catalog."
    >
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Card>
          <Paragraph>
            The backend pipeline writes through the documented Iceberg catalog wrapper and streams
            progress over the shared task WebSocket.
          </Paragraph>
          <Form
            layout="vertical"
            initialValues={{ format: "auto", namespace: "aqp", annotate: false }}
            onFinish={submit}
          >
            <Form.Item label="Source path" name="source_dir" rules={[{ required: true }]}>
              <Input placeholder="C:/Users/angel/Downloads/my_dataset" />
            </Form.Item>
            <Space wrap>
              <Form.Item label="Format" name="format">
                <Select
                  style={{ width: 160 }}
                  options={["auto", "csv", "parquet", "json", "ndjson"].map((value) => ({
                    value,
                    label: value,
                  }))}
                />
              </Form.Item>
              <Form.Item label="Namespace" name="namespace">
                <Input style={{ width: 180 }} />
              </Form.Item>
              <Form.Item label="Max rows" name="max_rows">
                <InputNumber min={1} style={{ width: 140 }} />
              </Form.Item>
              <Form.Item label="Max files" name="max_files">
                <InputNumber min={1} style={{ width: 140 }} />
              </Form.Item>
            </Space>
            <Button type="primary" htmlType="submit">
              Queue ingest
            </Button>
          </Form>
        </Card>

        {taskId ? (
          <Card title={`Task ${taskId}`}>
            <Text type="secondary">Status: {stream.status}</Text>
            <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>
              {stream.events.map((event, index) => `[${index}] ${JSON.stringify(event)}`).join("\n") ||
                "Waiting for progress..."}
            </pre>
          </Card>
        ) : null}
      </Space>
    </PageContainer>
  );
}
