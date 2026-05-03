"use client";

import { EntityDetail } from "./EntityDetail";

export function EntityDetailRouter({ entityId }: { entityId: string }) {
  return <EntityDetail entityId={entityId} />;
}
