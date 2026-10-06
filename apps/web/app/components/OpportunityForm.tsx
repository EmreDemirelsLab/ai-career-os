"use client";
import { useState, type FormEvent } from "react";

export default function OpportunityForm({ skills, onSaved }: { skills: string[]; onSaved: () => Promise<void> }) {
  const [requirements, setRequirements] = useState<number[]>([]);
  const [nextId, setNextId] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form);
    setBusy(true); setError(""); setNotice("");
    try {
      const response = await fetch("/api/workspace/opportunities", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: data.get("title"), company: data.get("company"),
          source_url: data.get("source_url"), observed_on: data.get("observed_on"),
          skills: data.getAll("skills"), review_notes: data.get("review_notes"),
          requirements: requirements.map(id => ({ kind: data.get(`kind-${id}`), value: data.get(`value-${id}`),
            evidence_span: data.get(`span-${id}`), mandatory: data.get(`mandatory-${id}`) === "on" })) }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Alanları ve tarihi kontrol et.");
      form.reset(); setRequirements([]); setNotice("İlan kaydedildi. Hazırlık paketini ilan kartından açabilirsin.");
      await onSaved();
    } catch (e) { setError(e instanceof Error ? e.message : "İlan kaydedilemedi."); }
    finally { setBusy(false); }
  }
  return <form onSubmit={submit}>
    {error && <p role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}
    <div className="grid">
      <label className="field"><span>İlan başlığı</span><input name="title" required maxLength={200} /></label>
      <label className="field"><span>Şirket</span><input name="company" required maxLength={200} /></label>
      <label className="field"><span>İlan bağlantısı</span><input name="source_url" type="url" required /></label>
      <label className="field"><span>İnceleme tarihi</span><input name="observed_on" type="date" required /></label>
      <label className="field"><span>Beceriler (çoklu seçim)</span><select name="skills" multiple size={5}>{skills.map(s => <option key={s}>{s}</option>)}</select></label>
    </div>
    <p>Yalnız ilanda açıkça yazan şartları, kısa kaynak metniyle ekle. Belirtilmeyen bilgi bilinmiyor olarak kalır.</p>
    {requirements.map((id, index) => <fieldset key={id}><legend>Şart {index + 1}</legend>
      <label className="field"><span>Şart türü {index + 1}</span><select name={`kind-${id}`}>
        <option value="german">Almanca</option><option value="english">İngilizce</option>
        <option value="degree">İlgili diploma</option><option value="experience">Profesyonel deneyim</option>
        <option value="work_authorization">Çalışma hakkı</option><option value="location">Konum</option>
      </select></label>
      <label className="field"><span>Gereken değer {index + 1} (B2, yes, yıl sayısı…)</span><input name={`value-${id}`} required maxLength={200} /></label>
      <label className="field"><span>Kaynak metni {index + 1}</span><textarea name={`span-${id}`} required maxLength={500} /></label>
      <label><input name={`mandatory-${id}`} type="checkbox" /> İlanda açıkça zorunlu ({index + 1})</label>
      <button type="button" disabled={busy} onClick={() => setRequirements(requirements.filter(x => x !== id))}>Şart {index + 1} kaldır</button>
    </fieldset>)}
    <button type="button" disabled={busy || requirements.length >= 20} onClick={() => { setRequirements([...requirements, nextId]); setNextId(nextId + 1); }}>Şart ekle</button>
    <label className="field"><span>İnceleme notun</span><textarea name="review_notes" required maxLength={10000} /></label>
    <button disabled={busy}>{busy ? "Kaydediliyor…" : "İlanı kaydet"}</button>
  </form>;
}
