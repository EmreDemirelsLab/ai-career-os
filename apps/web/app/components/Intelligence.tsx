"use client";
import { useEffect, useState, type FormEvent } from "react";

type RecordData = {
  id: string;
  kind: string;
  created_at: string;
  synthetic?: boolean;
  sample_size?: number;
  skill_counts?: Record<string, number>;
  sequence?: {
    id: string;
    skill: string;
    action: string;
    observed_job_mentions: number;
  }[];
  notice?: string;
  source_ids?: string[];
};
type Feedback = {
  id: string;
  status: string;
  assessment_status: string;
  feedback?: {
    technical_feedback: string;
    english_feedback: string;
    next_exercise: string;
    follow_up_question: string;
    limitations: string;
  };
  error_code?: string;
};
type State = {
  records: RecordData[];
  feedback: Feedback[];
  sources: { id: string; name: string; enabled: boolean }[];
  ai: {
    configured: boolean;
    model: string | null;
    used_today: number;
    daily_limit: number;
  };
};
type Props = {
  skills: string[];
  attempts: { id: string; week: number }[];
  interviews: { id: string; question: string }[];
};

export default function Intelligence({ skills, attempts, interviews }: Props) {
  const [data, setData] = useState<State | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState("");
  const [requestKey, setRequestKey] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    fetch("/api/workspace/intelligence", { cache: "no-store" })
      .then(async (r) => {
        if (!r.ok) throw new Error("Analiz verileri alınamadı.");
        const d = await r.json();
        if (active) setData(d);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, []);
  async function reload() {
    const r = await fetch("/api/workspace/intelligence", { cache: "no-store" });
    if (r.ok) setData(await r.json());
  }
  async function send(path: string, body: unknown) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const r = await fetch("/api/workspace/intelligence/" + path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const d = await r.json();
      if (!r.ok)
        throw new Error(
          typeof d.detail === "string" ? d.detail : "Alanları kontrol et.",
        );
      await reload();
      setNotice(
        d.status === "FAILED"
          ? "AI çağrısı tamamlanamadı. İstek geçmişini incele."
          : "Kayıt oluşturuldu.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function form(handler: (f: FormData) => void) {
    return (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      handler(new FormData(e.currentTarget));
    };
  }
  if (!data) return <section>{error || "Analiz alanı yükleniyor…"}</section>;
  const markets = data.records.filter((x) => x.kind === "market");
  return (
    <>
      <p className="lead">
        Kaynaklı piyasa örneklemi → beceri önkoşulları → bağımsız çalışma → geri
        bildirim.
      </p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
      <div className="grid">
        <section>
          <h2>Piyasa örneklemi</h2>
          <p>
            Önce operatör CLI ile onaylı kaynağı topla. Sentetik veri gerçek
            piyasa analizi değildir.
          </p>
          <form
            onSubmit={form(
              (f) =>
                void send("market", {
                  source_ids: f.getAll("sources"),
                  include_demo: f.get("demo") === "on",
                }),
            )}
          >
            <label className="field">
              Kaynaklar
              <select multiple name="sources" required>
                {data.sources
                  .filter((x) => x.enabled)
                  .map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.id})
                    </option>
                  ))}
              </select>
            </label>
            <label>
              <input type="checkbox" name="demo" /> Sentetik örneği açıkça dahil
              et
            </label>
            <button disabled={busy}>Piyasa snapshot oluştur</button>
          </form>
        </section>
        <section>
          <h2>Önkoşullu çalışma planı</h2>
          <p>
            Beceri önkoşulları korunur; hazır konular örneklemdeki anılma
            sayısına göre sıralanır. Bu, işe alınma veya yetkinlik puanı
            değildir.
          </p>
          <form
            onSubmit={form(
              (f) =>
                void send("plans", {
                  market_snapshot_id: f.get("market"),
                  target_skills: f.getAll("targets"),
                }),
            )}
          >
            <label className="field">
              Piyasa sürümü
              <select name="market" required>
                <option value="">Seç</option>
                {markets.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.synthetic ? "SENTETİK" : "Kaynaklı"} · {m.sample_size}{" "}
                    ilan · {m.created_at}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              Hedef beceriler
              <select multiple name="targets" required size={5}>
                {skills.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <button disabled={busy}>Önkoşullu plan oluştur</button>
          </form>
        </section>
      </div>
      {markets.map((m) => (
        <section key={m.id}>
          <h3>
            {m.synthetic
              ? "Sentetik örnek — piyasa kanıtı değil"
              : "Seçili kaynak örneklemi"}{" "}
            · {m.sample_size} ilan
          </h3>
          <p>
            Kaynaklar: {m.source_ids?.join(", ")}. Kelime eşleşmeleri zorunlu
            gereksinim sayılmaz; olumsuz ifadeler de anılma olarak geçebilir.
          </p>
          <table>
            <thead>
              <tr>
                <th>Beceri</th>
                <th>Anıldığı ilan</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(m.skill_counts || {}).map(([s, n]) => (
                <tr key={s}>
                  <td>{s}</td>
                  <td>{n}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
      {data.records
        .filter((x) => x.kind === "adaptive_plan")
        .map((p) => (
          <section key={p.id}>
            <h3>Plan · {new Date(p.created_at).toLocaleString("tr")}</h3>
            <ol>
              {p.sequence?.map((x) => (
                <li key={x.id}>
                  {x.skill} —{" "}
                  {x.action === "independent_recheck"
                    ? "bağımsız yeniden kontrol"
                    : "öğren ve kanıtla"}{" "}
                  ({x.observed_job_mentions} ilan)
                </li>
              ))}
            </ol>
            <p className="muted">{p.notice}</p>
          </section>
        ))}
      <section>
        <h2>AI öğretmen ve mülakat geri bildirimi</h2>
        <p>
          {data.ai.configured
            ? `Model: ${data.ai.model}. Bugün (UTC) kullanılan çağrı: ${data.ai.used_today}/${data.ai.daily_limit}.`
            : "AI kapalı. Sunucuda model, sağlayıcı anahtarı ve günlük çağrı sınırı yapılandırılmalı."}
        </p>
        <p>
          Yalnızca seçtiğin yanıt ve soru sağlayıcıya gönderilir. Teknik ve
          İngilizce geri bildirim ayrı üretilir; insan incelemesi gerektirir ve
          beceri kanıtı sayılmaz.
        </p>
        <form
          onChange={() => setRequestKey(null)}
          onSubmit={form((f) => {
            const [type, id] = String(f.get("target")).split(":");
            const key = requestKey || crypto.randomUUID();
            setRequestKey(key);
            void send("feedback", {
              target_type: type,
              target_id: id,
              request_key: key,
              consent_to_send: f.get("consent") === "on",
            });
          })}
        >
          <label className="field">
            Değerlendirilecek kayıt
            <select name="target" required>
              <option value="">Seç</option>
              {attempts.map((a) => (
                <option key={a.id} value={"learning:" + a.id}>
                  Öğrenme · Hafta {a.week} · {a.id.slice(0, 8)}
                </option>
              ))}
              {interviews.map((i) => (
                <option key={i.id} value={"interview:" + i.id}>
                  Mülakat · {i.question}
                </option>
              ))}
            </select>
          </label>
          <label>
            <input type="checkbox" name="consent" required /> Bu kaydın AI
            sağlayıcısına gönderilmesini onaylıyorum.
          </label>
          <button disabled={busy || !data.ai.configured}>
            AI geri bildirimi iste
          </button>
        </form>
        <p className="muted">
          Aynı formu tekrar göndermek aynı isteği kontrol eder. Başarısız
          çağrılar da günlük sınıra dahildir. Yeni istek için seçimi değiştir.
        </p>
      </section>
      {data.feedback.map((f) => (
        <section key={f.id}>
          <h3>AI taslağı · {f.status}</h3>
          {f.feedback ? (
            <>
              <h4>Teknik geri bildirim</h4>
              <p>{f.feedback.technical_feedback}</p>
              <h4>İngilizce geri bildirim</h4>
              <p>{f.feedback.english_feedback}</p>
              <h4>Bağımsız alıştırma</h4>
              <p>{f.feedback.next_exercise}</p>
              <h4>Takip sorusu</h4>
              <p>{f.feedback.follow_up_question}</p>
              <p className="muted">{f.feedback.limitations}</p>
            </>
          ) : (
            <p>
              {f.error_code ||
                "Sonuç bekleniyor; otomatik tekrar çağrı yapılmaz."}
            </p>
          )}
        </section>
      ))}
      <button onClick={() => void reload()}>Durumu yenile</button>
    </>
  );
}
