import { apiUrl } from "./config";

export type QueryValue = string | number | boolean | null | undefined;

export interface ApiFetchOptions extends Omit<RequestInit, "body"> {
  query?: Record<string, QueryValue>;
  body?: BodyInit | Record<string, unknown> | unknown[] | null;
}

function withQuery(path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(apiUrl(path));
  if (!query) return url.toString();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

export async function apiFetch<T = unknown>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const { query, headers, body, ...init } = options;
  const requestHeaders = new Headers(headers);
  let requestBody: BodyInit | undefined;

  if (body != null) {
    if (
      typeof body === "string" ||
      body instanceof Blob ||
      body instanceof FormData ||
      body instanceof URLSearchParams ||
      body instanceof ArrayBuffer
    ) {
      requestBody = body;
    } else {
      requestHeaders.set("content-type", requestHeaders.get("content-type") ?? "application/json");
      requestBody = JSON.stringify(body);
    }
  }

  const response = await fetch(withQuery(path, query), {
    ...init,
    headers: requestHeaders,
    body: requestBody,
    cache: init.cache ?? "no-store",
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: unknown; message?: unknown };
      detail = String(payload.detail ?? payload.message ?? detail);
    } catch {
      const text = await response.text().catch(() => "");
      if (text) detail = text;
    }
    throw new Error(detail);
  }

  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
}
