"use client";

import { useEffect, useMemo, useState } from "react";

import { wsUrl } from "@/lib/api/config";

export interface StreamEvent {
  task_id?: string;
  stage?: string;
  message?: string;
  timestamp?: string;
  token?: string;
  text?: string;
  agent?: string;
  tool?: string;
  delta?: string;
  content?: string;
  tool_output?: unknown;
  result?: unknown;
  error?: string;
  [key: string]: unknown;
}

export interface ChatStreamState {
  status: "idle" | "connecting" | "open" | "closed" | "error";
  events: StreamEvent[];
  text: string;
  done: boolean;
  error: string | null;
}

function eventText(event: StreamEvent): string {
  return String(event.token ?? event.text ?? "");
}

export function useChatStream(taskId: string | null | undefined): ChatStreamState {
  const [status, setStatus] = useState<ChatStreamState["status"]>("idle");
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [text, setText] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setEvents([]);
    setText("");
    setDone(false);
    setError(null);
    if (!taskId) {
      setStatus("idle");
      return;
    }

    setStatus("connecting");
    const socket = new WebSocket(wsUrl(`/chat/stream/${encodeURIComponent(taskId)}`));

    socket.onopen = () => setStatus("open");
    socket.onmessage = (message) => {
      let event: StreamEvent;
      try {
        event = JSON.parse(String(message.data)) as StreamEvent;
      } catch {
        event = { message: String(message.data) };
      }
      setEvents((current) => [...current, event]);
      const chunk = eventText(event);
      if (chunk) setText((current) => current + chunk);
      const stage = String(event.stage ?? "").toLowerCase();
      if (stage === "done" || stage === "completed" || event.done === true) setDone(true);
      if (event.error) {
        setError(String(event.error));
        setDone(true);
      }
    };
    socket.onerror = () => {
      setStatus("error");
      setError("WebSocket connection failed");
    };
    socket.onclose = () => {
      setStatus((current) => (current === "error" ? "error" : "closed"));
      setDone(true);
    };

    return () => socket.close();
  }, [taskId]);

  return useMemo(() => ({ status, events, text, done, error }), [status, events, text, done, error]);
}
