"use client";
import { useState } from "react";

export default function CareerPack({ opportunityId }: { opportunityId: string }) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function prepare() {
    setBusy(true); setError("");
    try {
      const response = await fetch(`/api/workspace/career-pack/${opportunityId}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Hazırlık paketi alınamadı.");
      setText((await response.json()).text);
    } catch (e) { setError(e instanceof Error ? e.message : "Paket hazırlanamadı."); }
    finally { setBusy(false); }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url; link.download = `career-preparation-${opportunityId}.txt`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <div>
    <button disabled={busy} onClick={prepare}>{busy ? "Hazırlanıyor…" : "Başvuru hazırlık paketini aç"}</button>
    {error && <p role="alert">{error}</p>}
    {text && <div>
      <p>Bu bir hazırlık taslağıdır. İlanı ve kendi iddialarını kontrol et; hiçbir başvuru gönderilmedi.</p>
      <textarea aria-label="Başvuru hazırlık paketi" readOnly value={text} rows={16} />
      <button onClick={download}>Hazırlık paketini indir</button>
    </div>}
  </div>;
}
