export type TaxInput = {
  gross_salary: number;
  deductions_80c: number;
  deductions_80d: number;
  hra_exemption?: number;
  regime_preference: "old" | "new";
};

const KEYS = {
  taxInput: "et_tax_input",
  taxResult: "et_tax_result",
  portfolioInput: "et_portfolio_input",
  portfolioResult: "et_portfolio_result",
  newsItems: "et_news_items",
  uploadPayload: "et_upload_payload",
  unifiedReport: "et_unified_report",
};

function saveJson(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value));
}

function loadJson<T>(key: string): T | null {
  const raw = localStorage.getItem(key);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function saveTaxInput(value: TaxInput) {
  saveJson(KEYS.taxInput, value);
}

export function loadTaxInput(): TaxInput | null {
  return loadJson<TaxInput>(KEYS.taxInput);
}

export function saveTaxResult(value: unknown) {
  saveJson(KEYS.taxResult, value);
}

export function loadTaxResult<T = unknown>(): T | null {
  return loadJson<T>(KEYS.taxResult);
}

export function savePortfolioInput(value: Array<Record<string, unknown>>) {
  saveJson(KEYS.portfolioInput, value);
}

export function loadPortfolioInput<T = Array<Record<string, unknown>>>(): T | null {
  return loadJson<T>(KEYS.portfolioInput);
}

export function savePortfolioResult(value: unknown) {
  saveJson(KEYS.portfolioResult, value);
}

export function loadPortfolioResult<T = unknown>(): T | null {
  return loadJson<T>(KEYS.portfolioResult);
}

export function saveNewsItems(value: Array<Record<string, unknown>>) {
  saveJson(KEYS.newsItems, value);
}

export function loadNewsItems<T = Array<Record<string, unknown>>>(): T | null {
  return loadJson<T>(KEYS.newsItems);
}

export function saveUploadPayload(value: unknown) {
  saveJson(KEYS.uploadPayload, value);
}

export function loadUploadPayload<T = unknown>(): T | null {
  return loadJson<T>(KEYS.uploadPayload);
}

export function saveUnifiedReport(value: unknown) {
  saveJson(KEYS.unifiedReport, value);
}

export function loadUnifiedReport<T = unknown>(): T | null {
  return loadJson<T>(KEYS.unifiedReport);
}
