"use client";

import { Tabs } from "antd";

import { EntityList } from "./EntityList";

export function KgTabs() {
  return (
    <Tabs
      defaultActiveKey="issuers"
      items={[
        {
          key: "issuers",
          label: "Issuers",
          children: <EntityList />,
        },
      ]}
    />
  );
}
