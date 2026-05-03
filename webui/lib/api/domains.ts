export interface StrategySummary {
  id: string;
  name: string;
  status?: string;
  asset_class?: string | null;
  tags?: string[];
  latest_version?: number | string | null;
  updated_at?: string | null;
}

export interface BacktestRunSummary {
  id: string;
  engine?: string;
  status?: string;
  started_at?: string | null;
  finished_at?: string | null;
  metrics?: Record<string, number | null | undefined>;
}

export interface PaperRunSummary {
  id: string;
  status?: string;
  config_path?: string;
  started_at?: string | null;
  stopped_at?: string | null;
}

export interface OrderRow {
  id: string;
  vt_symbol?: string;
  side?: string;
  quantity?: number;
  filled?: number;
  avg_fill_price?: number | null;
  status?: string;
  venue?: string;
  submitted_at?: string | null;
}

export interface FillRow {
  id: string;
  order_id?: string;
  vt_symbol?: string;
  price?: number;
  quantity?: number;
  venue?: string;
  timestamp?: string | null;
}

export interface PositionRow {
  vt_symbol: string;
  quantity?: number;
  avg_price?: number;
  last_price?: number;
  market_value?: number;
  unrealized_pnl?: number;
}

export interface LedgerEntryRow {
  id?: string;
  timestamp?: string | null;
  account?: string;
  type?: string;
  amount?: number;
  balance_after?: number;
  description?: string;
}

export interface DataSourceSummary {
  id?: string;
  name: string;
  vendor?: string;
  status?: string;
  description?: string;
}

export interface CrewRunSummary {
  task_id: string;
  crew?: string;
  status?: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface MlModelSummary {
  id?: string;
  name: string;
  framework?: string;
  status?: string;
  metrics?: Record<string, number | null | undefined>;
}
