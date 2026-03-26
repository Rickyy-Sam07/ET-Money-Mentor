import { useEffect, useState } from "react";
import { ensureSession, getProfile } from "../lib/api";

export function DashboardPage() {
  const [sessionId, setSessionId] = useState<string>("");
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    async function load() {
      const sid = await ensureSession();
      setSessionId(sid);
      const user = await getProfile();
      setProfile(user.profile);
    }

    void load();
  }, []);

  return (
    <section className="card">
      <h2>Dashboard</h2>
      <p className="muted">
        Disclaimer: This information is for educational purposes only. Consult a SEBI-registered advisor before investment decisions.
      </p>
      <p><strong>Session:</strong> {sessionId || "Loading..."}</p>
      <pre className="output-box">{JSON.stringify(profile, null, 2)}</pre>
    </section>
  );
}
