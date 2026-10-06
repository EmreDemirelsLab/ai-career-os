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
- P3a branch: `feat/retention-maintenance` (PR #4: https://github.com/EmreDemirelsLab/ai-career-os/pull/4)
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

Yerel Ruff/format/mypy geçti; pytest 34 passed / 30 skipped (PostgreSQL yok). İlk PostgreSQL CI: 58 passed / 6 skipped; bakım testleri geçti. Compose restore, verisi olmayan onaysız seed kaynaklarını da bakım fonksiyonuna gönderdiği için durdu. Restore artık yalnız raw verisi bulunan gerçek kaynakları seçiyor; verisi olup politikası eksik kaynak hâlâ fail-closed. Düzeltme head 2cd9f634 üzerinde PR run 37401610008 ile doğrulandı; tüm joblar başarılı. PR #4 incelemeye hazır.

## Çalışma ortamı ve kurtarma

Önceki checkout: `/workspace/scratch/0ce556516ccd/ai-career-os`. Scratch kaybolabilir; GitHub kalıcı doğruluk kaynağıdır. Local commit SHA'ları connector ile oluşturulmuş remote SHA'lardan farklı olabilir; local history'yi force-push etme. Remote base tree + commit + fast-forward ref yöntemi kullanıldı. Yeni oturumda local/remote diff'i kontrol et; tamamlanmış dosyaları tekrar üretme.

`uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest -q`; web için `npm ci`, `npm run lint`, `npm run typecheck`, `npm run build`. PostgreSQL/Docker/browser ve restore sonuçlarını CI'dan doğrula; SQLite geçişini eşdeğer sayma.

## Gerçek engeller / açık işler

Kaynak-specific review ve gerçek piyasa/gold seti, worker/recovery kodu, doğrulanmış ders/assessment içeriği, canlı model seçimi-kullanım sınırı-eval, son kariyer çıktı akışları, gerçek hosting/domain/TLS/monitoring/offsite backup ve kullanıcı kabulü açık. Bunların tümü yalnızca API anahtarı eksikliği değildir. Secret istemek yerine ilgili environment/secret store üzerinden kurulum yap.

## P3b1 checkpoint — 2026-10-06

P3a remote head `2cd9f63471ac84839037df4289824ccbdc17c7a0`: PR run 37401610008 completed SUCCESS, including Python, web, Compose/browser and restore. PR #4 ready for review, not merged.

Active branch `feat/collection-scheduling`, stacked on P3a. Migration 0005, PostgreSQL bounded scheduler and metadata queue, CLI and concurrency tests implemented. No worker/network/cron. See docs/27_COLLECTION_SCHEDULING.md. Local Ruff/format/mypy pass; pytest 35 passed / 41 skipped (PostgreSQL unavailable). PR #5: https://github.com/EmreDemirelsLab/ai-career-os/pull/5. Initial remote code head d63afbb7b91f324410fe3460dec6405a690aadce. CI runs 37402092895 / 37402088816 started. Next: verify latest-head PostgreSQL CI, fix failures, record exact head/run. Then P3b2 worker/recovery per docs27. Full product and live-data/model/hosting gates remain open.

## P3b2 active checkpoint

P3b1 head `360653972198dc82f43158c5040380e3174f7a69`: PR run 37402154444 all jobs SUCCESS; PR #5 ready for review, not merged.
Active branch now `feat/collection-worker`, stacked on P3b1. Worker/recovery and synthetic failure/concurrency tests implemented; see docs28. Local Ruff/format/mypy pass, pytest 35 passed / 55 skipped; PG worker tests require CI. Next: open stacked PR, verify exact head/run, fix failures. No live source collection, cron installation, model call or deployment.

P3b2 PR #6: https://github.com/EmreDemirelsLab/ai-career-os/pull/6. Initial head 83a8c11b8a65524d431744f501c72b90569cefed; CI runs 37402411276 / 37402407343. Added orphaned RUNNING ingestion recovery test; check latest remote head after test commit before declaring this slice verified.
