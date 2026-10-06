# AI Career OS — devam kaydı

Güncelleme: 2026-10-06, Europe/Istanbul.

## Amaç ve yetki

Kullanıcının sistemi tamamen bitirme isteği sürüyor. İş artık [parçalı teslim planına](docs/25_DELIVERY_PLAN.md) göre ilerleyecek. Repo yazımı ve PR açma yetkili; otomatik merge, ücretli kaynak açma veya deployment yapılmadı. Gizli anahtarları sohbet/PR/dosyaya açık olarak yazma.

## Önce okunacaklar

`AGENTS.md`, `docs/25_DELIVERY_PLAN.md`, `docs/23_INTELLIGENCE_RELEASE.md`, `docs/24_HOSTING_RUNBOOK.md`. Eski belgeler tarihsel tasarımı korur; uygulanmış özellikler için güncel override belgelerini kullan.

## GitHub durumu

- Repo: https://github.com/EmreDemirelsLab/ai-career-os
- PR #1 foundation: https://github.com/EmreDemirelsLab/ai-career-os/pull/1
- PR #2 workspace: https://github.com/EmreDemirelsLab/ai-career-os/pull/2 (base #1 branch)
- Önceki PR #3: https://github.com/EmreDemirelsLab/ai-career-os/pull/3 (base `feat/career-workspace`)
- Aktif branch: `feat/retention-maintenance` (P3a; PR açılacak)
- P2 kod head'i: `d934411f562d0aef79634bc27cc86c39f2c1abbd`
- Bu kayıt PR merge edildiğini varsaymaz; devam ederken remote branch/PR durumunu yeniden oku.

## Uygulanan P2

Greenhouse operator collector; kaynak span'lı literal mention analizi; sürümlü market snapshot; önkoşul DAG ve deterministik plan; consent + quota + idempotency içeren AI feedback gateway; hash'li, süreli ve iptal edilebilir sunucu session; Analiz & AI ekranı; yedek/checksum/disposable restore; Caddy + restricted runtime DB rolü içeren hosted aday. Migration head `0003_intelligence`.

AI gateway testleri mocked transport kullanır; canlı model veya gerçek ilan toplama yapılmadı. Mention analizi semantic requirement extraction değildir. Auth tek kullanıcılıdır. Retention window seçimi raw silme anlamına gelmez. Bu parça tam ürün tamamlanması değildir.

## Doğrulama

- Yerel Ruff/format/mypy ve frontend lint/typecheck/build geçti.
- Yerel pytest: 33 geçti, 23 atlandı (PostgreSQL yok; SQLite varyantlarında PostgreSQL-only concurrency atlanır).
- Önceki P2 CI: Python ve web geçti; browser kaynak seçicinin etiketinde durdu. `aria-label` ile düzeltildi.
- Son P2 head'i CI: [PR run](https://github.com/EmreDemirelsLab/ai-career-os/actions/runs/37380977411), [push run](https://github.com/EmreDemirelsLab/ai-career-os/actions/runs/37380972149). Push run tamamlandı: tüm job’lar başarılı. 53 Python testi geçti, 3 PostgreSQL-only concurrency SQLite varyantı atlandı; 1 Playwright testi geçti. Restricted-role DDL reddi, hosted/Caddy config doğrulaması, Compose, backup/checksum/restore ve restored kayıt sayısı kontrolü geçti. Canlı TLS/model/ilan toplama doğrulanmadı.

## Aktif P3a çalışma notu

Kaynak: docs/26_RETENTION_CONTRACT.md. `0004_retention` migration, dar PostgreSQL SECURITY DEFINER fonksiyonu, raw DELETE bakım istisnası (owner + function context), normal UPDATE yasağı, içeriksiz audit ve CLI yazıldı. Market/plan üretimi bakım ile advisory transaction lock paylaşır. Bağlı market/plan silinir; learner kayıtları korunur. Restore drill yalnız disposable DB'de retention uygular. Gerçek veri üzerinde bakım çalıştırılmadı.

Yerel Ruff/format/mypy geçti; pytest 34 passed / 30 skipped (PostgreSQL yok). PostgreSQL silme/rol/rollback/replay/refresh testleri henüz CI'da doğrulanmadı. Bu nedenle P3a tamamlanmış sayılmaz.

## Sıradaki işlem

1. P3a branch'ini PR #3 branch'ine karşı PR yap ve PostgreSQL/Compose CI'yı çalıştır.
2. SQL/permission/restore hatası varsa logdan düzelt; veri silme yalnız disposable CI fixture'larında çalışacak.
3. Yeşil CI sonrası exact commit/run/test sayısını kaydet. Sonraki P3b scheduling/recovery parçasına geç.

## Çalışma ortamı ve kurtarma

Önceki checkout: `/workspace/scratch/0ce556516ccd/ai-career-os`. Scratch kaybolabilir; GitHub kalıcı doğruluk kaynağıdır. Local commit SHA'ları connector ile oluşturulmuş remote SHA'lardan farklı olabilir; local history'yi force-push etme. Remote base tree + commit + fast-forward ref yöntemi kullanıldı. Yeni oturumda local/remote diff'i kontrol et; tamamlanmış dosyaları tekrar üretme.

`uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest -q`; web için `npm ci`, `npm run lint`, `npm run typecheck`, `npm run build`. PostgreSQL/Docker/browser ve restore sonuçlarını CI'dan doğrula; SQLite geçişini eşdeğer sayma.

## Gerçek engeller / açık işler

Kaynak-specific review ve gerçek piyasa/gold seti, retention/scheduling kodu, doğrulanmış ders/assessment içeriği, canlı model seçimi-kullanım sınırı-eval, son kariyer çıktı akışları, gerçek hosting/domain/TLS/monitoring/offsite backup ve kullanıcı kabulü açık. Bunların tümü yalnızca API anahtarı eksikliği değildir. Secret istemek yerine ilgili environment/secret store üzerinden kurulum yap.
