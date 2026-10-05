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
