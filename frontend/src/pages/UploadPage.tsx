// [DEV1] UploadPage.tsx — document upload with OCR + manual edit. Dev2: do not modify.
import { ChangeEvent, useState } from "react";
import { uploadDocument } from "../lib/api";
import { saveUploadPayload } from "../lib/voiceState";

type Form16Fields = {
  employer: string;
  pan: string;
  gross_salary: string;
  basic_salary: string;
  hra: string;
  special_allowance: string;
  deductions_80c: string;
  deductions_80d: string;
  deductions_80e: string;
  deductions_hra_exemption: string;
  tds_deducted: string;
  assessment_year: string;
};

type FundRow = {
  name: string;
  units: string;
  nav: string;
  invested_amount: string;
  buy_date: string;
  expense_ratio: string;
};

const EMPTY_FORM16: Form16Fields = {
  employer: "", pan: "", gross_salary: "", basic_salary: "",
  hra: "", special_allowance: "", deductions_80c: "", deductions_80d: "",
  deductions_80e: "", deductions_hra_exemption: "", tds_deducted: "", assessment_year: "",
};

const EMPTY_FUND: FundRow = {
  name: "", units: "", nav: "", invested_amount: "", buy_date: "", expense_ratio: "",
};

function toStr(v: unknown): string {
  if (v === null || v === undefined) return "";
  return String(v);
}

function fieldsToForm16(fields: Record<string, unknown>): Form16Fields {
  return {
    employer: toStr(fields.employer),
    pan: toStr(fields.pan),
    gross_salary: toStr(fields.gross_salary),
    basic_salary: toStr(fields.basic_salary),
    hra: toStr(fields.hra),
    special_allowance: toStr(fields.special_allowance),
    deductions_80c: toStr(fields.deductions_80c),
    deductions_80d: toStr(fields.deductions_80d),
    deductions_80e: toStr(fields.deductions_80e),
    deductions_hra_exemption: toStr(fields.deductions_hra_exemption),
    tds_deducted: toStr(fields.tds_deducted),
    assessment_year: toStr(fields.assessment_year),
  };
}

function fieldsToFunds(fields: Record<string, unknown>): FundRow[] {
  const raw = Array.isArray(fields.funds) ? fields.funds : [];
  if (raw.length === 0) return [{ ...EMPTY_FUND }];
  return raw.map((f: any) => ({
    name: toStr(f.name),
    units: toStr(f.units),
    nav: toStr(f.nav),
    invested_amount: toStr(f.invested_amount),
    buy_date: toStr(f.buy_date),
    expense_ratio: toStr(f.expense_ratio),
  }));
}

export function UploadPage() {
  const [docType, setDocType] = useState<"form16" | "portfolio_statement" | null>(null);
  const [form16, setForm16] = useState<Form16Fields>({ ...EMPTY_FORM16 });
  const [funds, setFunds] = useState<FundRow[]>([{ ...EMPTY_FUND }]);
  const [rawPreview, setRawPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  async function onChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setSaved(false);
    try {
      const data = await uploadDocument(file);
      const fields = data?.parsed?.extracted_fields ?? data?.extracted_fields ?? {};
      const type = data?.parsed?.document_type ?? data?.document_type ?? "form16";
      setDocType(type);
      setRawPreview(toStr(data?.parsed?.raw_text_preview ?? data?.raw_text_preview ?? ""));
      if (type === "form16") {
        setForm16(fieldsToForm16(fields));
      } else {
        setFunds(fieldsToFunds(fields));
      }
    } finally {
      setLoading(false);
    }
  }

  function updateForm16(key: keyof Form16Fields, value: string) {
    setForm16((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function updateFund(idx: number, key: keyof FundRow, value: string) {
    setFunds((prev) => prev.map((f, i) => i === idx ? { ...f, [key]: value } : f));
    setSaved(false);
  }

  function addFundRow() {
    setFunds((prev) => [...prev, { ...EMPTY_FUND }]);
  }

  function removeFundRow(idx: number) {
    setFunds((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleSave() {
    const payload = docType === "form16"
      ? { document_type: "form16", extracted_fields: form16 }
      : { document_type: "portfolio_statement", extracted_fields: { funds } };
    saveUploadPayload({ parsed: payload });
    setSaved(true);
  }

  const form16Labels: { key: keyof Form16Fields; label: string }[] = [
    { key: "employer", label: "Employer Name" },
    { key: "pan", label: "PAN" },
    { key: "assessment_year", label: "Assessment Year" },
    { key: "gross_salary", label: "Gross Salary (₹)" },
    { key: "basic_salary", label: "Basic Salary (₹)" },
    { key: "hra", label: "HRA Received (₹)" },
    { key: "special_allowance", label: "Special Allowance (₹)" },
    { key: "deductions_80c", label: "80C Deductions (₹)" },
    { key: "deductions_80d", label: "80D Deductions (₹)" },
    { key: "deductions_80e", label: "80E Deductions (₹)" },
    { key: "deductions_hra_exemption", label: "HRA Exemption (₹)" },
    { key: "tds_deducted", label: "TDS Deducted (₹)" },
  ];

  return (
    <section className="card">
      <h2>Document Upload</h2>
      <p className="muted">Supports PDF, PNG, JPG, JPEG, WEBP, TXT. OCR text is parsed by AI — missing fields are left blank for you to fill.</p>

      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
        onChange={onChange}
        className="upload-input"
      />

      {loading && <p>Extracting fields via OCR + AI...</p>}

      {docType === "form16" && (
        <div className="insight-panel">
          <h3>Form 16 — Extracted Fields</h3>
          <p className="muted">Fields left blank were not found in the document. Please fill them manually.</p>
          <div className="upload-form-grid">
            {form16Labels.map(({ key, label }) => (
              <label key={key} className="upload-field-label">
                <span>{label}</span>
                <input
                  value={form16[key]}
                  onChange={(e) => updateForm16(key, e.target.value)}
                  placeholder="Not found — enter manually"
                  className={form16[key] ? "upload-field-filled" : "upload-field-empty"}
                />
              </label>
            ))}
          </div>
          <button type="button" className="upload-save-btn" onClick={handleSave}>
            {saved ? "✓ Saved" : "Save & Use This Data"}
          </button>
        </div>
      )}

      {docType === "portfolio_statement" && (
        <div className="insight-panel">
          <h3>Portfolio Statement — Extracted Funds</h3>
          <p className="muted">Fields left blank were not found in the document. Please fill them manually.</p>
          <div className="table-wrap">
            <table className="portfolio-input-table">
              <thead>
                <tr>
                  <th>Fund Name</th>
                  <th>Units</th>
                  <th>NAV (₹)</th>
                  <th>Invested (₹)</th>
                  <th>Buy Date</th>
                  <th>Exp. Ratio (%)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {funds.map((f, idx) => (
                  <tr key={idx}>
                    {(["name", "units", "nav", "invested_amount", "buy_date", "expense_ratio"] as (keyof FundRow)[]).map((col) => (
                      <td key={col}>
                        <input
                          value={f[col]}
                          onChange={(e) => updateFund(idx, col, e.target.value)}
                          placeholder="—"
                          className={f[col] ? "upload-field-filled" : "upload-field-empty"}
                        />
                      </td>
                    ))}
                    <td>
                      <button type="button" onClick={() => removeFundRow(idx)} className="upload-remove-btn">✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="upload-table-actions">
            <button type="button" className="upload-add-btn" onClick={addFundRow}>+ Add Row</button>
            <button type="button" className="upload-save-btn" onClick={handleSave}>
              {saved ? "✓ Saved" : "Save & Use This Data"}
            </button>
          </div>
        </div>
      )}

      {rawPreview && (
        <details className="raw-json-panel">
          <summary>Raw OCR Text Preview</summary>
          <pre className="output-box">{rawPreview}</pre>
        </details>
      )}
    </section>
  );
}
