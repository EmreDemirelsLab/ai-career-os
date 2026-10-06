"use client";
import Intelligence from "./components/Intelligence";
import Lessons from "./components/Lessons";
import CareerPack from "./components/CareerPack";
import OpportunityForm from "./components/OpportunityForm";
import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";

type Unit = {
  week: number;
  title: string;
  skill: string;
  why: string;
  build: string;
  english_question: string;
  source_url: string;
  source_checked_on: string;
  stages: string[];
};
type Profile = {
  name: string;
  target_role: string;
  weekly_hours: number;
  english: string;
  german: string;
  location: string;
  work_authorization: string;
  relevant_degree: string;
  professional_years: number | null;
};
type Evidence = {
  id: string;
  skill: string;
  dimension: string;
  artifact_url: string;
  assistance: string;
  verifier: string;
  notes: string;
};
type Opportunity = {
  id: string;
  title: string;
  company: string;
  source_url: string;
  observed_on: string;
  skills: string[];
  fit: {
    eligibility: string;
    unverified_skills: string[];
    checks: { kind: string; status: string; evidence_span: string }[];
  };
};
type Workspace = {
  profile: Profile | null;
  profile_versions: number;
  skills: string[];
  curriculum: { units: Unit[] };
  evidence: Evidence[];
  roadmaps: { id: string; created_at: string; weekly_hours: number }[];
  attempts: {
    id: string;
    week: number;
    concept_answer: string;
    english_answer: string;
  }[];
  review_queue: {
    attempt_id: string;
    week: number;
    interval: number;
    due_at: string;
  }[];
  interviews: { id: string; question: string; answer: string }[];
  opportunities: Opportunity[];
  applications: { id: string; opportunity_id: string; cv_version: string }[];
  application_events: {
    id: string;
    application_id: string;
    stage: string;
    created_at: string;
  }[];
};
const tabs = [
  "Bugün",
  "Profil",
  "24 haftalık plan",
  "Öğren & İngilizce",
  "Temel alıştırmalar",
  "Kanıtlar",
  "Mülakat",
  "Fırsatlar",
  "Başvurular",
  "Analiz & AI",
  "Veri kontrolü",
];
const levels = ["unknown", "none", "A1", "A2", "B1", "B2", "C1", "C2"];
function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}
function Link({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children} ↗
    </a>
  );
}
const string = (f: FormData, k: string) => String(f.get(k) || "");

export default function Home() {
  const [data, setData] = useState<Workspace | null>(null),
    [tab, setTab] = useState("Bugün"),
    [week, setWeek] = useState(1),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [token, setToken] = useState("");
  const load = useCallback(async () => {
    try {
      const r = await fetch("/api/workspace", { cache: "no-store" });
      if (r.status === 401) {
        setData(null);
        return;
      }
      if (!r.ok)
        throw new Error(
          "Çalışma alanına ulaşılamıyor. API bağlantısını kontrol et.",
        );
      setData(await r.json());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    let active = true;
    fetch("/api/workspace", { cache: "no-store" })
      .then(async (r) => {
        if (!active) return;
        if (r.status === 401) return;
        if (!r.ok) throw new Error("Çalışma alanına ulaşılamıyor.");
        const value = await r.json();
        if (active) setData(value);
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  async function mutate(path: string, payload: unknown) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const r = await fetch(`/api/workspace/${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) {
        const e = await r.json();
        throw new Error(
          typeof e.detail === "string"
            ? e.detail
            : "Alanları kontrol et; kayıt doğrulanamadı.",
        );
      }
      await load();
      setNotice("Kaydedildi.");
      return true;
    } catch (e) {
      setError((e as Error).message);
      return false;
    } finally {
      setBusy(false);
    }
  }
  function submit(handler: (form: FormData) => Promise<unknown>) {
    return (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      void handler(new FormData(event.currentTarget));
    };
  }
  async function login(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
      });
      if (!r.ok) throw new Error((await r.json()).detail);
      setToken("");
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (loading)
    return (
      <main className="login">
        <p>Çalışma alanı yükleniyor…</p>
      </main>
    );
  if (!data)
    return (
      <main className="login">
        <p className="eyebrow">AI CAREER OS</p>
        <h1>
          Öğren.
          <br />
          Üret. Kanıtla.
        </h1>
        <p>
          AI mühendisliği, teknik İngilizce ve kariyer çalışmaların için kişisel
          alanın.
        </p>
        <form onSubmit={login}>
          <Field label="Kişisel erişim anahtarı">
            <input
              type="password"
              autoComplete="off"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
              minLength={32}
            />
          </Field>
          <button disabled={busy}>Çalışma alanını aç</button>
        </form>
        <p className="muted">
          Anahtar, yerel kurulumda oluşturduğun .env dosyasındaki
          CAREER_API_TOKEN değeridir.
        </p>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
      </main>
    );
  const unit = data.curriculum.units.find((x) => x.week === week)!;
  const due = data.review_queue.filter((x) => new Date(x.due_at) <= new Date());
  const button = (
    <button disabled={busy} type="submit">
      Kaydet
    </button>
  );
  return (
    <div className="shell">
      <aside>
        <div className="brand">
          AI CAREER<span>OS</span>
        </div>
        <p className="muted">Kişisel çalışma alanı</p>
        <nav aria-label="Ana menü">
          {tabs.map((t) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => {
                setTab(t);
                setError("");
                setNotice("");
              }}
            >
              {t}
            </button>
          ))}
        </nav>
        <button
          className="logout"
          onClick={async () => {
            const r = await fetch("/api/session", { method: "DELETE" });
            if (r.ok) setData(null);
            else setError("Oturum kapatılamadı; tekrar dene.");
          }}
        >
          Oturumu kapat
        </button>
      </aside>
      <main className="content">
        <header>
          <div>
            <p className="eyebrow">BUILD · EXPLAIN · IMPROVE</p>
            <h1>{tab}</h1>
          </div>
          <span className="badge">Kişisel sürüm</span>
        </header>
        <div className="connection">
          Canlı kaynak ve AI yapılandırmasını Analiz & AI alanından kontrol et.
          Bu alandaki çalışmalar ve kayıtlar kalıcı olarak saklanır.
        </div>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {notice && (
          <p className="success" role="status">
            {notice}
          </p>
        )}
        {tab === "Bugün" && (
          <>
            <h2>
              {data.profile
                ? `${data.profile.name}, sıradaki kanıtını üret.`
                : "Önce hedefini tanımla."}
            </h2>
            <p className="lead">
              Bir konuyu anlamak, uygulamak ve İngilizce savunmak. Her çalışma
              bir sonraki adıma dayanak olsun.
            </p>
            <div className="stats">
              <section>
                <strong>{data.evidence.length}</strong>
                <span>Kanıt kaydı</span>
              </section>
              <section>
                <strong>{data.attempts.length}</strong>
                <span>Öğrenme gönderimi</span>
              </section>
              <section>
                <strong>{due.length}</strong>
                <span>Günü gelen tekrar</span>
              </section>
              <section>
                <strong>{data.applications.length}</strong>
                <span>Başvuru kaydı</span>
              </section>
            </div>
            <div className="grid">
              <section>
                <h2>Bugünün çalışma döngüsü</h2>
                <ol>
                  <li>Nedenini kendi cümlelerinle anlat.</li>
                  <li>Küçük bir örnek uygula ve test et.</li>
                  <li>İngilizce bir mühendislik kararını savun.</li>
                  <li>Kanıtını ekle, tekrarını planla.</li>
                </ol>
                <button
                  onClick={() =>
                    setTab(data.profile ? "Temel alıştırmalar" : "Profil")
                  }
                >
                  Başla →
                </button>
              </section>
              <section>
                <h2>Gecikmiş tekrarlar</h2>
                {due.length === 0 ? (
                  <p>
                    Henüz günü gelen tekrar yok. Öğrenme gönderimleri 3, 7, 14
                    ve 30 gün için tekrar oluşturur.
                  </p>
                ) : (
                  due.map((x) => (
                    <form
                      key={x.attempt_id + x.interval}
                      onSubmit={submit((f) =>
                        mutate("reviews", {
                          attempt_id: x.attempt_id,
                          interval: x.interval,
                          notes: string(f, "notes"),
                        }),
                      )}
                    >
                      <p>
                        Hafta {x.week} · {x.interval}. gün
                      </p>
                      <textarea
                        name="notes"
                        placeholder="Kaynağa bakmadan hatırladıklarını yaz."
                        required
                        maxLength={10000}
                      />
                      {button}
                    </form>
                  ))
                )}
              </section>
            </div>
            <p className="muted">
              Kayıt sayıları beceri puanı değildir. Bağımsız değerlendirme henüz
              yapılmadı.
            </p>
          </>
        )}
        {tab === "Profil" && (
          <section>
            <h2>Hedef ve çalışma koşulları</h2>
            <p>
              Her kayıt yeni profil sürümü oluşturur. Bilmediğin uygunluk
              alanlarını “unknown” bırak.
            </p>
            <form
              key={data.profile_versions}
              onSubmit={submit((f) =>
                mutate("profile", {
                  name: string(f, "name"),
                  target_role: string(f, "target_role"),
                  weekly_hours: Number(f.get("weekly_hours")),
                  english: string(f, "english"),
                  german: string(f, "german"),
                  location: string(f, "location"),
                  work_authorization: string(f, "work_authorization"),
                  relevant_degree: string(f, "relevant_degree"),
                  professional_years:
                    string(f, "professional_years") === ""
                      ? null
                      : Number(f.get("professional_years")),
                }),
              )}
            >
              <div className="grid">
                <Field label="Adın">
                  <input
                    name="name"
                    defaultValue={data.profile?.name || ""}
                    required
                    maxLength={200}
                  />
                </Field>
                <Field label="Hedef rol">
                  <select
                    name="target_role"
                    defaultValue={
                      data.profile?.target_role || "APPLIED_AI_ENGINEER"
                    }
                  >
                    {[
                      "AI_ENGINEER",
                      "APPLIED_AI_ENGINEER",
                      "ML_ENGINEER",
                      "LLM_ENGINEER",
                    ].map((x) => (
                      <option key={x}>{x}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Haftalık ayırabileceğin saat">
                  <input
                    type="number"
                    name="weekly_hours"
                    min={1}
                    max={60}
                    defaultValue={data.profile?.weekly_hours}
                    required
                  />
                </Field>
                <Field label="Yaşadığın yer">
                  <input
                    name="location"
                    defaultValue={data.profile?.location || ""}
                    required
                    maxLength={200}
                  />
                </Field>
                {["english", "german"].map((x) => (
                  <Field
                    key={x}
                    label={
                      x === "english" ? "İngilizce seviyen" : "Almanca seviyen"
                    }
                  >
                    <select
                      name={x}
                      defaultValue={
                        data.profile?.[x as "english" | "german"] || "unknown"
                      }
                    >
                      {levels.map((y) => (
                        <option key={y}>{y}</option>
                      ))}
                    </select>
                  </Field>
                ))}
                {["work_authorization", "relevant_degree"].map((x) => (
                  <Field
                    key={x}
                    label={
                      x === "work_authorization"
                        ? "Hedef ülkede çalışma izni"
                        : "İlgili diploma"
                    }
                  >
                    <select
                      name={x}
                      defaultValue={
                        data.profile?.[
                          x as "work_authorization" | "relevant_degree"
                        ] || "unknown"
                      }
                    >
                      {["unknown", "yes", "no"].map((y) => (
                        <option key={y}>{y}</option>
                      ))}
                    </select>
                  </Field>
                ))}
                <Field label="Profesyonel deneyim yılı (bilinmiyorsa boş)">
                  <input
                    name="professional_years"
                    type="number"
                    min={0}
                    max={60}
                    defaultValue={data.profile?.professional_years ?? ""}
                  />
                </Field>
              </div>
              {button}
            </form>
          </section>
        )}
        {tab === "24 haftalık plan" && (
          <>
            <section>
              <h2>Temel rota</h2>
              <p>
                Bu sıralama başlangıç müfredatıdır; henüz canlı piyasa verisine
                göre uyarlanmıyor. Her hafta bir çalışma paketi, takvim
                garantisi değil.
              </p>
              <button
                disabled={busy || !data.profile}
                onClick={() => void mutate("roadmaps", {})}
              >
                Profille planın sürümünü kaydet
              </button>
              <p className="muted">
                {data.roadmaps.length} plan sürümü kayıtlı. Profilini
                değiştirmek eski planı değiştirmez.
              </p>
            </section>
            <div className="grid">
              {data.curriculum.units.map((u) => (
                <section key={u.week}>
                  <p className="eyebrow">
                    HAFTA {String(u.week).padStart(2, "0")}
                  </p>
                  <h2>{u.title}</h2>
                  <p>{u.build}</p>
                  <span className="tag">{u.skill}</span>
                  <button
                    className="text-button"
                    onClick={() => {
                      setWeek(u.week);
                      setTab("Temel alıştırmalar");
                    }}
                  >
                    Çalışma paketini aç →
                  </button>
                </section>
              ))}
            </div>
          </>
        )}
        {tab === "Öğren & İngilizce" && (
          <>
            <Field label="Çalışma paketi">
              <select
                value={week}
                onChange={(e) => setWeek(Number(e.target.value))}
              >
                {data.curriculum.units.map((u) => (
                  <option key={u.week} value={u.week}>
                    {u.week}. {u.title}
                  </option>
                ))}
              </select>
            </Field>
            <div className="grid">
              <section>
                <p className="eyebrow">NEDEN?</p>
                <h2>{unit.title}</h2>
                <p>{unit.why}</p>
                <ol>
                  {unit.stages.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ol>
                <h3>Üreteceğin çalışma</h3>
                <p>{unit.build}</p>
                <Link href={unit.source_url}>Resmî başlangıç kaynağı</Link>
                <p className="muted">
                  Kontrol: {unit.source_checked_on}. Kaynak ilgili başlıkları
                  araştırmak için başlangıç noktasıdır.
                </p>
              </section>
              <section>
                <p className="eyebrow">TEKNİK İNGİLİZCE</p>
                <h2>{unit.english_question}</h2>
                <p>
                  Yanıtında şu sırayı dene: “I chose… because… The trade-off is…
                  I verified it by…”
                </p>
                <form
                  onSubmit={submit((f) =>
                    mutate("learning", {
                      week,
                      concept_answer: string(f, "concept_answer"),
                      english_answer: string(f, "english_answer"),
                      artifact_url: string(f, "artifact_url") || null,
                    }),
                  )}
                >
                  <Field label="Türkçe kavram açıklaman">
                    <textarea
                      name="concept_answer"
                      required
                      maxLength={10000}
                    />
                  </Field>
                  <Field label="İngilizce teknik açıklaman">
                    <textarea
                      name="english_answer"
                      required
                      maxLength={10000}
                    />
                  </Field>
                  <Field label="Çalışma bağlantısı (isteğe bağlı)">
                    <input type="url" name="artifact_url" />
                  </Field>
                  {button}
                </form>
                <p className="muted">
                  Gönderim saklanır ve tekrar planlanır; otomatik başarı veya
                  ustalık puanı verilmez.
                </p>
              </section>
            </div>
            <section>
              <h2>Önceki gönderimlerin</h2>
              {data.attempts
                .filter((x) => x.week === week)
                .map((x) => (
                  <details key={x.id}>
                    <summary>{x.english_answer.slice(0, 90)}</summary>
                    <p>{x.concept_answer}</p>
                    <p>{x.english_answer}</p>
                  </details>
                ))}
            </section>
          </>
        )}
        {tab === "Kanıtlar" && (
          <>
            <section>
              <h2>Çalışmanı bir beceriye bağla</h2>
              <form
                onSubmit={submit((f) =>
                  mutate("evidence", {
                    skill: string(f, "skill"),
                    dimension: string(f, "dimension"),
                    artifact_url: string(f, "artifact_url"),
                    notes: string(f, "notes"),
                    assistance: string(f, "assistance"),
                    verifier: string(f, "verifier"),
                    review_reference: string(f, "review_reference") || null,
                  }),
                )}
              >
                <div className="grid">
                  <Field label="Beceri">
                    <select aria-label="Beceri" name="skill">
                      {data.skills.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Boyut">
                    <select name="dimension">
                      {[
                        "conceptual",
                        "implementation",
                        "debugging",
                        "production",
                        "system_design",
                        "explanation",
                        "interview",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Çalışma bağlantısı">
                    <input type="url" name="artifact_url" required />
                  </Field>
                  <Field label="Yardım düzeyi">
                    <select name="assistance">
                      {["assisted", "independent", "generated"].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Doğrulama kaynağı">
                    <select name="verifier">
                      <option>self_report</option>
                      <option>external_review</option>
                    </select>
                  </Field>
                  <Field label="Dış değerlendirme bağlantısı">
                    <input type="url" name="review_reference" />
                  </Field>
                </div>
                <Field label="Neyi yaptın, neyi kanıtlıyor, sınırı ne?">
                  <textarea name="notes" required maxLength={10000} />
                </Field>
                {button}
              </form>
            </section>
            <div className="grid">
              {data.evidence.map((e) => (
                <section key={e.id}>
                  <span className="tag">{e.dimension}</span>
                  <h2>{e.skill}</h2>
                  <p>{e.notes}</p>
                  <p className="muted">
                    {e.assistance} · {e.verifier} · kullanıcı beyanı
                  </p>
                  <Link href={e.artifact_url}>Kanıtı aç</Link>
                </section>
              ))}
            </div>
          </>
        )}
        {tab === "Mülakat" && (
          <>
            <section>
              <h2>İngilizce proje savunması</h2>
              <p>
                Teknik doğruluk, kanıt, alternatifler ve sınırları açıkla.
                Ardından İngilizce açıklığın, yapın ve terim kullanımını ayrı
                değerlendir. Kaydettiğin yanıt için Analiz & AI alanından geri
                bildirim isteyebilirsin.
              </p>
              <form
                onSubmit={submit((f) =>
                  mutate("interviews", {
                    question_id: string(f, "question_id"),
                    answer: string(f, "answer"),
                  }),
                )}
              >
                <Field label="Soru">
                  <select name="question_id">
                    {data.curriculum.units.map((u) => (
                      <option key={u.week} value={u.week}>
                        {u.english_question}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="İngilizce yanıtın">
                  <textarea name="answer" required maxLength={10000} />
                </Field>
                {button}
              </form>
            </section>
            {data.interviews.map((i) => (
              <section key={i.id}>
                <h3>{i.question}</h3>
                <p>{i.answer}</p>
                <span className="tag">Değerlendirme bekliyor</span>
              </section>
            ))}
          </>
        )}
        {tab === "Fırsatlar" && (
          <>
            <section>
              <h2>İncelediğin ilanı kaydet</h2>
              <p>
                Bunlar senin kaynaklı inceleme notların; piyasa istatistiği
                değildir. Belirtilmeyen şartları zorunlu kabul etme.
              </p>
              <OpportunityForm skills={data.skills} onSaved={load} />
            </section>
            <div className="grid">
              {data.opportunities.map((o) => (
                <section key={o.id}>
                  <span className="tag">{o.fit.eligibility}</span>
                  <h2>{o.title}</h2>
                  <p>
                    {o.company} · {o.observed_on}
                  </p>
                  <Link href={o.source_url}>Kaynak ilan</Link>
                  <CareerPack opportunityId={o.id} />
                  {o.fit.checks.map((c, i) => (
                    <p key={i}>
                      {c.kind}: {c.status} — {c.evidence_span}
                    </p>
                  ))}
                  <p>
                    Bağımsız dış değerlendirme bağlantısı eksik beceriler:{" "}
                    {o.fit.unverified_skills.join(", ") || "Kayıt yok"}
                  </p>
                  <p className="muted">
                    Sonuç girilen şartlarla sınırlıdır; işe alım kararı veya
                    doğrulanmış yeterlilik değildir.
                  </p>
                </section>
              ))}
            </div>
          </>
        )}
        {tab === "Başvurular" && (
          <>
            <section>
              <h2>Başvuru kaydı</h2>
              <form
                onSubmit={submit((f) =>
                  mutate("applications", {
                    opportunity_id: string(f, "opportunity_id"),
                    cv_version: string(f, "cv_version"),
                    notes: string(f, "notes"),
                  }),
                )}
              >
                <Field label="Kayıtlı fırsat">
                  <select aria-label="Kayıtlı fırsat" name="opportunity_id" required>
                    <option value="">Seç</option>
                    {data.opportunities.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.company} — {o.title}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="CV sürümü">
                  <input name="cv_version" required maxLength={200} />
                </Field>
                <Field label="Not">
                  <textarea name="notes" maxLength={5000} />
                </Field>
                {button}
              </form>
            </section>
            {data.applications.map((a) => (
              <section key={a.id}>
                <h2>
                  {
                    data.opportunities.find((o) => o.id === a.opportunity_id)
                      ?.title
                  }
                </h2>
                <p>CV: {a.cv_version}</p>
                <ol>
                  {data.application_events
                    .filter((e) => e.application_id === a.id)
                    .map((e) => (
                      <li key={e.id}>
                        {e.stage} ·{" "}
                        {new Date(e.created_at).toLocaleDateString("tr")}
                      </li>
                    ))}
                </ol>
                <form
                  onSubmit={submit((f) =>
                    mutate(`applications/${a.id}/events`, {
                      stage: string(f, "stage"),
                      notes: string(f, "notes"),
                    }),
                  )}
                >
                  <Field label="Yeni aşama">
                    <select aria-label="Yeni aşama" name="stage">
                      {[
                        "applied",
                        "screening",
                        "technical",
                        "offer",
                        "rejected",
                        "withdrawn",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Geri bildirim">
                    <textarea name="notes" maxLength={5000} />
                  </Field>
                  {button}
                </form>
              </section>
            ))}
          </>
        )}
        {tab === "Temel alıştırmalar" && <Lessons onSaved={load} initialWeek={week} />}
        {tab === "Analiz & AI" && (
          <Intelligence
            skills={data.skills}
            attempts={data.attempts}
            interviews={data.interviews}
          />
        )}
        {tab === "Veri kontrolü" && (
          <section>
            <h2>Verilerin senin kontrolünde</h2>
            <p>
              Profil sürümleri, gönderimler, kanıtlar, görüşmeler ve başvuru
              geçmişini dışa aktarabilirsin. Bu sürüm tek kişilik yerel kullanım
              içindir.
            </p>
            <button
              onClick={async () => {
                const r = await fetch("/api/workspace/export");
                if (!r.ok) {
                  setError("Dışa aktarma başarısız.");
                  return;
                }
                const blob = await r.blob(),
                  url = URL.createObjectURL(blob),
                  a = document.createElement("a");
                a.href = url;
                a.download = "ai-career-os-personal-export.json";
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Verilerimi indir
            </button>
            <hr />
            <h3>Kişisel çalışma alanını sil</h3>
            <p>
              Silme geri alınamaz. Profil, plan, kanıt ve tüm çalışma geçmişi
              silinir; kaynak ingestion verisine dokunulmaz.
            </p>
            <button
              className="danger"
              disabled={busy}
              onClick={async () => {
                if (
                  !window.confirm(
                    "Tüm kişisel çalışma kayıtları silinsin mi? Bu işlem geri alınamaz.",
                  )
                )
                  return;
                setBusy(true);
                try {
                  const r = await fetch("/api/workspace", {
                    method: "DELETE",
                    headers: {
                      "X-Confirm-Delete": "delete-personal-workspace",
                    },
                  });
                  if (!r.ok) throw new Error("Silme başarısız.");
                  await load();
                  setNotice("Kişisel çalışma alanı silindi.");
                } catch (e) {
                  setError((e as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              Kişisel verilerimi sil
            </button>
          </section>
        )}
      </main>
    </div>
  );
}
