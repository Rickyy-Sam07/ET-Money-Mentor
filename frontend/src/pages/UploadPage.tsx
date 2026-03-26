import { ChangeEvent, useState } from "react";
import { uploadDocument } from "../lib/api";

export function UploadPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function onChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setLoading(true);
    try {
      const data = await uploadDocument(file);
      setResult(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Document Upload</h2>
      <input type="file" accept=".pdf,.png,.jpg,.jpeg,.txt" onChange={onChange} />
      {loading ? <p>Extracting fields...</p> : null}
      <pre className="output-box">{result ? JSON.stringify(result, null, 2) : "No file uploaded yet."}</pre>
    </section>
  );
}
