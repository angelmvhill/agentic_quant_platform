"use client";

import { create } from "zustand";

export interface PageContext {
  page?: string;
  vt_symbol?: string;
  backtest_id?: string;
  strategy_id?: string;
  [key: string]: string | number | boolean | null | undefined;
}

interface PageContextState {
  context: PageContext;
  setContext: (patch: PageContext) => void;
  clearContext: () => void;
}

export const usePageContextStore = create<PageContextState>((set) => ({
  context: {},
  setContext: (patch) =>
    set((state) => {
      const next = { ...state.context };
      Object.entries(patch).forEach(([key, value]) => {
        if (value === undefined || value === null) {
          delete next[key];
        } else {
          next[key] = value;
        }
      });
      return { context: next };
    }),
  clearContext: () => set({ context: {} }),
}));
