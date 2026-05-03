"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemeMode = "light" | "dark";

interface UiState {
  themeMode: ThemeMode;
  sidebarCollapsed: boolean;
  assistantOpen: boolean;
  commandPaletteOpen: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setAssistantOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      themeMode: "dark",
      sidebarCollapsed: false,
      assistantOpen: false,
      commandPaletteOpen: false,
      toggleTheme: () =>
        set((state) => ({ themeMode: state.themeMode === "dark" ? "light" : "dark" })),
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setAssistantOpen: (assistantOpen) => set({ assistantOpen }),
      setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
    }),
    {
      name: "aqp-ui",
      partialize: (state) => ({
        themeMode: state.themeMode,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    },
  ),
);
