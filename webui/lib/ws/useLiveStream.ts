"use client";

import { useEffect, useMemo, useState } from "react";

import { wsUrl } from "@/lib/api/config";

export interface LiveStreamEvent {
  kind?: string;
  vt_symbol?: string;
  timestamp?: string;
  direction?: string;
  close?: number;
  [key: string]: unknown;
}

export interface LiveBar extends LiveStreamEvent {
  kind: "bar";
  vt_symbol: string;
  close: number;
}

export interface LiveQuote extends LiveStreamEvent {
  kind: "quote";
  vt_symbol: string;
  bid_close: number;
  ask_close: number;
}

export interface LiveTick extends LiveStreamEvent {
  kind: "tick";
  vt_symbol: string;
  last: number;
}

export interface LiveSignal extends LiveStreamEvent {
  kind: "signal";
  vt_symbol: string;
}

export type LiveMessage = LiveBar | LiveQuote | LiveTick | LiveSignal;

export interface LiveStreamState {
  status: "idle" | "connecting" | "open" | "closed" | "error";
  buffer: LiveMessage[];
  latest: Record<string, LiveMessage>;
  error: string | null;
}

export function useLiveStream({
  channelId,
  bufferSize = 128,
}: {
  channelId?: string | null;
  bufferSize?: number;
}): LiveStreamState {
  const [status, setStatus] = useState<LiveStreamState["status"]>("idle");
  const [buffer, setBuffer] = useState<LiveMessage[]>([]);
  const [latest, setLatest] = useState<Record<string, LiveMessage>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setBuffer([]);
    setLatest({});
    setError(null);
    if (!channelId) {
      setStatus("idle");
      return;
    }

    setStatus("connecting");
    const socket = new WebSocket(wsUrl(`/live/stream/${encodeURIComponent(channelId)}`));
    socket.onopen = () => setStatus("open");
    socket.onmessage = (message) => {
      let event: LiveMessage;
      try {
        event = JSON.parse(String(message.data)) as LiveMessage;
      } catch {
        event = { kind: "signal", vt_symbol: "unknown", message: String(message.data) };
      }
      setBuffer((current) => [...current, event].slice(-bufferSize));
      const symbol = typeof event.vt_symbol === "string" ? event.vt_symbol : undefined;
      if (symbol) setLatest((current) => ({ ...current, [symbol]: event }));
    };
    socket.onerror = () => {
      setStatus("error");
      setError("WebSocket connection failed");
    };
    socket.onclose = () => setStatus((current) => (current === "error" ? "error" : "closed"));
    return () => socket.close();
  }, [channelId, bufferSize]);

  return useMemo(() => ({ status, buffer, latest, error }), [status, buffer, latest, error]);
}
