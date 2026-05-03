export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.AQP_API_URL ||
  "http://localhost:8000"
).replace(/\/+$/, "");

export const WS_BASE_URL = (
  process.env.NEXT_PUBLIC_WS_URL ||
  process.env.AQP_WS_URL ||
  API_BASE_URL.replace(/^http:/, "ws:").replace(/^https:/, "wss:")
).replace(/\/+$/, "");

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}

export function wsUrl(path: string): string {
  if (/^wss?:\/\//i.test(path)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${WS_BASE_URL}${normalized}`;
}
