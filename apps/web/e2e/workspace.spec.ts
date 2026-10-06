import { test, expect } from "@playwright/test";

test("private workspace persists profile, roadmap and learning without certifying mastery", async ({
  page,
  request,
}) => {
  const token = process.env.CAREER_API_TOKEN;
  if (!token)
    throw new Error("Use a disposable workspace with CAREER_API_TOKEN");
  const rejected = await request.post("/api/session", {
    data: { token },
    headers: { origin: "https://untrusted.example" },
  });
  expect(rejected.status()).toBe(403);
  expect((await request.get("/api/workspace")).status()).toBe(401);
  await page.goto("/");
  await page
    .getByLabel("Kişisel erişim anahtarı")
    .fill("incorrect-key-with-more-than-32-characters");
  await page.getByRole("button", { name: "Çalışma alanını aç" }).click();
  await expect(
    page.getByText("Anahtar doğrulanamadı.", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Kişisel erişim anahtarı").fill(token);
  await page.getByRole("button", { name: "Çalışma alanını aç" }).click();
  await expect(
    page.getByRole("heading", { name: "Bugün", exact: true }),
  ).toBeVisible();
  const cookies = await page.context().cookies();
  expect(cookies.find((c) => c.name === "career_session")?.httpOnly).toBe(true);
  const sessionToken = cookies.find((c) => c.name === "career_session")!.value;
  expect(sessionToken).not.toBe(token);
  await page.getByRole("button", { name: "Profil", exact: true }).click();
  await page.getByLabel("Adın", { exact: true }).fill("Synthetic E2E learner");
  await page.getByLabel("Haftalık ayırabileceğin saat").fill("12");
  await page.getByLabel("Yaşadığın yer").fill("Test city");
  await page.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Kaydedildi.");
  await page
    .getByRole("button", { name: "24 haftalık plan", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Profille planın sürümünü kaydet" })
    .click();
  await expect(page.getByRole("status")).toHaveText("Kaydedildi.");
  await page
    .getByRole("button", { name: "Öğren & İngilizce", exact: true })
    .click();
  await page
    .getByLabel("Türkçe kavram açıklaman")
    .fill("Sentetik test açıklaması");
  await page
    .getByLabel("İngilizce teknik açıklaman")
    .fill("I verified the behavior with a test.");
  await page.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Kaydedildi.");
  await page.reload();
  await expect(
    page.getByRole("heading", {
      name: "Synthetic E2E learner, sıradaki kanıtını üret.",
    }),
  ).toBeVisible();
  const exported = await page.request.get("/api/workspace/export");
  expect(exported.ok()).toBe(true);
  const data = await exported.json();
  expect(data.roadmaps).toHaveLength(1);
  expect(data.attempts[0].assessment_status).toBe("submitted_unassessed");
  expect(data.review_queue).toHaveLength(4);
  expect(data.evidence).toHaveLength(0);
  await page.getByRole("button", { name: "Temel alıştırmalar", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Python: güvenilmeyen veriye sınır koy", exact: true })).toBeVisible();
  await page.getByLabel("Metin türünü denetle, trim et, boşluğu reddet", { exact: true }).check();
  await page.getByLabel("Hata gizlenir ve yanlış veri işlenebilir", { exact: true }).check();
  await page.getByLabel("Kendi sözlerinle teknik açıklama").fill("Önce tür, sonra trim ve boşluk kontrolü.");
  await page.getByLabel("İngilizce savunman").fill("I reject empty titles before persistence.");
  await page.getByRole("button", { name: "Tanı yanıtını kaydet" }).click();
  await expect(page.getByRole("heading", { name: "Tanı kaydedildi: 2/2" })).toBeVisible();
  const lessonExport = await (await page.request.get("/api/workspace/export")).json();
  expect(lessonExport.attempts).toHaveLength(2);
  expect(lessonExport.review_queue).toHaveLength(8);
  expect(lessonExport.evidence).toHaveLength(0);
  await page.reload();
  await page.getByRole("button", { name: "Temel alıştırmalar", exact: true }).click();
  await expect(page.getByRole("listitem").filter({ hasText: "ustalık doğrulanmadı" })).toHaveCount(1);
  await page.getByRole("button", { name: "24 haftalık plan", exact: true }).click();
  const finalWeek = page.locator("section").filter({ has: page.getByRole("heading", { name: "Portfolyo ve mülakat", exact: true }) });
  await finalWeek.getByRole("button", { name: "Çalışma paketini aç →", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Portfolyo: iddiadan artifacte", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Fırsatlar", exact: true }).click();
  await page.getByLabel("İlan başlığı", { exact: true }).fill("Synthetic AI Engineer");
  await page.getByLabel("Şirket", { exact: true }).fill("Synthetic Employer");
  await page.getByLabel("İlan bağlantısı", { exact: true }).fill("https://example.com/job");
  await page.getByLabel("İnceleme tarihi", { exact: true }).fill(new Date().toISOString().slice(0, 10));
  await page.getByLabel("Beceriler (çoklu seçim)", { exact: true }).selectOption("Python");
  await page.getByRole("button", { name: "Şart ekle", exact: true }).click();
  await page.getByLabel("Şart türü 1", { exact: true }).selectOption("english");
  await page.getByLabel("Gereken değer 1 (B2, yes, yıl sayısı…)", { exact: true }).fill("B2");
  await page.getByLabel("Kaynak metni 1", { exact: true }).fill("English B2 required");
  await page.getByLabel("İlanda açıkça zorunlu (1)", { exact: true }).check();
  await page.getByRole("button", { name: "Şart ekle", exact: true }).click();
  await page.getByLabel("Şart türü 2", { exact: true }).selectOption("degree");
  await page.getByLabel("Gereken değer 2 (B2, yes, yıl sayısı…)", { exact: true }).fill("yes");
  await page.getByLabel("Kaynak metni 2", { exact: true }).fill("Degree preferred");
  await page.getByLabel("İnceleme notun", { exact: true }).fill("Synthetic browser acceptance only");
  await page.getByRole("button", { name: "İlanı kaydet", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Synthetic AI Engineer", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Başvuru hazırlık paketini aç", exact: true }).click();
  await expect(page.getByLabel("Başvuru hazırlık paketi", { exact: true })).toHaveValue(/No relevant evidence recorded/);
  const packetDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Hazırlık paketini indir", exact: true }).click();
  expect((await packetDownload).suggestedFilename()).toMatch(/^career-preparation-.*\.txt$/);
  await page.getByRole("button", { name: "Kanıtlar", exact: true }).click();
  await page.getByLabel("Beceri", { exact: true }).selectOption("Python");
  await page.getByLabel("Çalışma bağlantısı", { exact: true }).fill("https://example.com/synthetic-artifact");
  await page.getByLabel("Neyi yaptın, neyi kanıtlıyor, sınırı ne?", { exact: true }).fill("Synthetic input validation exercise; assistance disclosed.");
  await page.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Kaydedildi.");
  await page.getByRole("button", { name: "Mülakat", exact: true }).click();
  await page.getByLabel("İngilizce yanıtın", { exact: true }).fill("I validate input before persistence. This synthetic example does not prove production competence.");
  await page.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(page.getByText("Değerlendirme bekliyor", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Fırsatlar", exact: true }).click();
  await page.getByRole("button", { name: "Başvuru hazırlık paketini aç", exact: true }).click();
  await expect(page.getByLabel("Başvuru hazırlık paketi", { exact: true })).toHaveValue(/synthetic-artifact/);
  await page.getByRole("button", { name: "Başvurular", exact: true }).click();
  await page.getByLabel("Kayıtlı fırsat", { exact: true }).selectOption({ index: 1 });
  await page.getByLabel("CV sürümü", { exact: true }).fill("synthetic-v1");
  await page.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Synthetic AI Engineer", exact: true })).toBeVisible();
  const applicationCard = page.locator("section").filter({ has: page.getByRole("heading", { name: "Synthetic AI Engineer", exact: true }) });
  await applicationCard.getByLabel("Yeni aşama", { exact: true }).selectOption("technical");
  await applicationCard.getByLabel("Geri bildirim", { exact: true }).fill("Synthetic interview invitation; no external message sent.");
  await applicationCard.getByRole("button", { name: "Kaydet", exact: true }).click();
  await expect(applicationCard.getByRole("listitem").filter({ hasText: "technical" })).toBeVisible();
  const careerExport = await (await page.request.get("/api/workspace/export")).json();
  expect(careerExport.evidence).toHaveLength(1);
  expect(careerExport.interviews).toHaveLength(1);
  expect(careerExport.applications).toHaveLength(1);
  expect(careerExport.opportunities[0].requirements).toHaveLength(2);
  await page.getByRole("button", { name: "Analiz & AI", exact: true }).click();
  await page.getByLabel("Kaynaklar", { exact: true }).selectOption("DEMO");
  await page.getByLabel("Sentetik örneği açıkça dahil et").check();
  await page.getByRole("button", { name: "Piyasa snapshot oluştur" }).click();
  await expect(
    page.getByRole("heading", {
      name: "Sentetik örnek — piyasa kanıtı değil · 2 ilan",
    }),
  ).toBeVisible();
  await page.getByLabel("Piyasa sürümü").selectOption({ index: 1 });
  await page.getByLabel("Hedef beceriler").selectOption("FastAPI");
  await page.getByRole("button", { name: "Önkoşullu plan oluştur" }).click();
  await expect(
    page
      .getByRole("listitem")
      .filter({ hasText: "FastAPI — öğren ve kanıtla" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "AI geri bildirimi iste" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Oturumu kapat" }).click();
  await expect(page.getByLabel("Kişisel erişim anahtarı")).toBeVisible();
  expect((await page.request.get("/api/workspace")).status()).toBe(401);
  const revoked = await request.get("http://localhost:8000/workspace", {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  expect(revoked.status()).toBe(401);
});
