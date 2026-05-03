"use client";

import { useMutation, useQuery, type QueryKey, type UseMutationOptions, type UseQueryOptions } from "@tanstack/react-query";

import { apiFetch, type ApiFetchOptions, type QueryValue } from "./client";

type ApiQueryOptions<TData, TSelected = TData> = Omit<
  UseQueryOptions<TData, Error, TSelected, QueryKey>,
  "queryFn"
> & {
  path: string;
  query?: Record<string, QueryValue>;
  request?: ApiFetchOptions;
};

export function useApiQuery<TData = unknown, TSelected = TData>({
  path,
  query,
  request,
  queryKey,
  ...options
}: ApiQueryOptions<TData, TSelected>) {
  return useQuery<TData, Error, TSelected, QueryKey>({
    queryKey,
    queryFn: () => apiFetch<TData>(path, { ...request, query }),
    ...options,
  });
}

type ApiMutationConfig<TVars, TData> = Omit<UseMutationOptions<TData, Error, TVars>, "mutationFn"> & {
  path: string | ((vars: TVars) => string);
  method?: string;
  query?: (vars: TVars) => Record<string, QueryValue>;
  toBody?: (vars: TVars) => unknown;
};

export function useApiMutation<TVars = Record<string, unknown>, TData = unknown>(
  config: ApiMutationConfig<TVars, TData>,
) {
  const { path, method, query, toBody, ...options } = config;
  return useMutation<TData, Error, TVars>({
    mutationFn: (vars) => {
      const resolvedPath = typeof path === "function" ? path(vars) : path;
      return apiFetch<TData>(resolvedPath, {
        method: method ?? "POST",
        query: query?.(vars),
        body: (toBody ? toBody(vars) : vars) as ApiFetchOptions["body"],
      });
    },
    ...options,
  });
}
