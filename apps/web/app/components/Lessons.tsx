"use client";
import { useEffect, useState, type FormEvent } from "react";

type Question = { id: string; prompt: string; choices: string[] };
type Lesson = {
  id: string; week: number; title: string; skill: string; why: string; explanation: string;
  worked_example: string; exercise: string; debug_prompt: string; english_prompt: string;
  english_terms: [string, string][]; source_url: string; source_checked_on: string;
  lab_command: string; questions: Question[]; technical_rubric: string[]; english_rubric: string[];
};
type Attempt = {
  id: string; lesson_title: string; assistance: string; objective_correct: number; objective_total: number;
  objective_checks: { question_id: string; prompt: string; correct: boolean; explanation: string }[];
};
type Practice = { suggested_lesson_id: string | null; scope: string; items: {
  lesson_id: string; title: string; state: string; reason: string;
}[] };
type Data = { catalog: { version: string; units: Lesson[] }; attempts: Attempt[]; practice: Practice | null };

export default function Lessons({ onSaved, initialWeek = 1 }: { onSaved: () => Promise<void>; initialWeek?: number }) {
  const [data, setData] = useState<Data | null>(null);
  const [selected, setSelected] = useState("foundation-1");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Attempt | null>(null);
  useEffect(() => {
    let active = true;
    fetch("/api/workspace/lessons", { cache: "no-store" }).then(async r => {
      if (!r.ok) throw new Error("Dersler alınamadı.");
      const value = await r.json();
      if (active) { setData(value); setSelected(value.catalog.units.find((x: Lesson) => x.week === initialWeek)?.id || "foundation-1"); }
    }).catch(e => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [initialWeek]);
  const lesson = data?.catalog.units.find(x => x.id === selected);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!lesson || !data) return;
    const form = new FormData(event.currentTarget);
    setBusy(true); setError(""); setResult(null);
    try {
      const response = await fetch("/api/workspace/lessons/attempts", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson_id: lesson.id, lesson_version: data.catalog.version,
          answers: Object.fromEntries(lesson.questions.map(q => [q.id, Number(form.get(q.id))])),
          concept_answer: form.get("concept_answer"), english_answer: form.get("english_answer"),
          assistance: form.get("assistance"), artifact_url: form.get("artifact_url") || null }),
      });
      const value = await response.json();
      if (!response.ok) throw new Error(typeof value.detail === "string" ? value.detail : "Yanıtlarını kontrol et.");
      setResult(value); setData({ ...data, attempts: [value, ...data.attempts].slice(0, 50), practice: null });
      const refreshed = await fetch("/api/workspace/lessons", { cache: "no-store" });
      if (!refreshed.ok) throw new Error("Yanıt kaydedildi; öneriler yenilenemedi. Sayfayı yenile.");
      setData(await refreshed.json());
      await onSaved();
    } catch (e) { setError(e instanceof Error ? e.message : "Kayıt yapılamadı."); }
    finally { setBusy(false); }
  }
  if (!lesson || !data) return <p role="status">{error || "Dersler yükleniyor…"}</p>;
  return <section>
    <h2>Temel alıştırmalar</h2>
    <p>24 haftaya yayılmış kavram, küçük lab ve İngilizce savunma paketleri. Kısa sorular tanı içindir; doğru cevaplar ustalık veya İngilizce seviyesi kanıtı değildir.</p>
    {error && <p role="alert">{error}</p>}
    {data.practice && <aside className="card" aria-label="Çalışma önerisi">
      <h3>Sıradaki çalışma</h3><p>{data.practice.scope}</p>
      {data.practice.items.filter(x => x.lesson_id === data.practice?.suggested_lesson_id).map(x => <div key={x.lesson_id}>
        <strong>{x.title}</strong><p>{x.reason}</p>
        <button type="button" disabled={busy} onClick={() => { setSelected(x.lesson_id); setResult(null); }}>Önerilen dersi aç</button>
      </div>)}
      <details><summary>Derslerin çalışma durumu</summary><ul>{data.practice.items.map(x => <li key={x.lesson_id}><strong>{x.title}</strong> — {x.reason}</li>)}</ul></details>
    </aside>}
    <label className="field"><span>Ders seç</span><select value={selected} disabled={busy} onChange={e => { setSelected(e.target.value); setResult(null); }}>
      {data.catalog.units.map(x => <option key={x.id} value={x.id}>{x.week}. hafta — {x.title}</option>)}
    </select></label>
    <article className="card">
      <h3>{lesson.title}</h3><h4>Neden?</h4><p>{lesson.why}</p>
      <h4>Kavramı kur</h4><p>{lesson.explanation}</p>
      <h4>Somut örnek</h4><p>{lesson.worked_example}</p>
      <h4>Kendin uygula</h4><p>{lesson.exercise}</p><pre className="lesson-code"><code>{lesson.lab_command}</code></pre>
      <p>Komutu yerel repo klasöründe çalıştır. Başlangıç kodunun testi sen uygulayana kadar başarısız olur. Sunucu gönderdiğin kodu çalıştırmaz.</p>
      <h4>Hatayı bul</h4><p>{lesson.debug_prompt}</p>
      <a href={lesson.source_url} target="_blank" rel="noopener noreferrer">Resmî okuma kaynağı ↗</a><small> — kontrol: {lesson.source_checked_on}</small>
      <h4>Teknik İngilizce</h4><p>{lesson.english_prompt}</p>
      <dl>{lesson.english_terms.map(([term, meaning]) => <div key={term}><dt>{term}</dt><dd>{meaning}</dd></div>)}</dl>
      <details><summary>Bağımsız savunma ölçütleri</summary>
        <h4>Teknik</h4><ul>{lesson.technical_rubric.map(x => <li key={x}>{x}</li>)}</ul>
        <h4>İngilizce</h4><ul>{lesson.english_rubric.map(x => <li key={x}>{x}</li>)}</ul>
      </details>
    </article>
    <form key={lesson.id} onSubmit={submit} className="card">
      <h3>Anladığını kontrol et</h3>
      {lesson.questions.map(q => <fieldset key={q.id}><legend>{q.prompt}</legend>
        {q.choices.map((choice, i) => <label key={choice} className="field"><span><input type="radio" required name={q.id} value={i} /> {choice}</span></label>)}
      </fieldset>)}
      <label className="field"><span>Kendi sözlerinle teknik açıklama</span><textarea name="concept_answer" required maxLength={10000} /></label>
      <label className="field"><span>İngilizce savunman</span><textarea name="english_answer" required maxLength={10000} /></label>
      <label className="field"><span>Bu denemede yardım düzeyi</span><select name="assistance" defaultValue="assisted">
        <option value="assisted">Yardım aldım</option><option value="independent">Bağımsız yaptım (öz bildirim)</option><option value="generated">Çözüm üretildi / kopyalandı</option>
      </select></label>
      <label className="field"><span>Alıştırma veya test kanıtı bağlantısı (isteğe bağlı)</span><input name="artifact_url" type="url" /></label>
      <button disabled={busy}>{busy ? "Kaydediliyor…" : "Tanı yanıtını kaydet"}</button>
    </form>
    {result && <div className="card" role="status"><h3>Tanı kaydedildi: {result.objective_correct}/{result.objective_total}</h3>
      <p>Yalnız seçenekli sorular kontrol edildi. Kodun ve İngilizce savunman bağımsız değerlendirme bekliyor. Tekrar tarihlerin çalışma alanına eklendi.</p>
      {result.objective_checks.map(x => <p key={x.question_id}><strong>{x.correct ? "Doğru" : "Tekrar çalış"}:</strong> {x.prompt} — {x.explanation}</p>)}
    </div>}
    <h3>Son ders denemeleri</h3>
    <ul>{data.attempts.map(x => <li key={x.id}>{x.lesson_title} — {x.objective_correct}/{x.objective_total}; yardım: {x.assistance}; ustalık doğrulanmadı</li>)}</ul>
  </section>;
}
