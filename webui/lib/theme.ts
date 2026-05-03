import { theme, type ThemeConfig } from "antd";

import type { ThemeMode } from "./store/ui";

export function buildTheme(mode: ThemeMode): ThemeConfig {
  const dark = mode === "dark";
  return {
    algorithm: dark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: "#4f8cff",
      borderRadius: 8,
      fontFamily:
        "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    },
    components: {
      Layout: {
        bodyBg: dark ? "#080b12" : "#f6f8fb",
        siderBg: dark ? "#0d111a" : "#ffffff",
        headerBg: dark ? "#0d111a" : "#ffffff",
      },
      Card: {
        headerBg: "transparent",
      },
    },
  };
}
