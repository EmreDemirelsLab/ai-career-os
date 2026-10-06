# AI Career OS — devam kaydı

2026-10-06. Kullanıcı: sistemi parçalara bölerek tamamla; kaldığın yeri kalıcı notlarla koru. Repo yazımı ve PR açma yetkili. Otomatik merge/deployment yok. Kullanıcının hedefi altı ay içinde Almanya/Avrupa AI/ML/Applied AI rollerine hazırlanmak; üretilen kod bağımsız öğrenme kanıtı değildir.

## Devam ederken

Önce AGENTS.md, docs/25_DELIVERY_PLAN.md ve aktif parçanın sözleşmesini oku. Remote head/CI'yı doğrula. Yerel çalışmaların remote ile aynı commit geçmişine sahip olduğunu varsayma; force-push yapma. Tam ürün bitti deme: P3c–P7 gerçek veri/model, öğrenme içeriği, kariyer çıktıları ve canlı operasyon kabulü açık.

## Repo ve doğrulanmış parçalar

Repo: https://github.com/EmreDemirelsLab/ai-career-os

| Parça | PR / branch | Kanıt |
| --- | --- | --- |
| Foundation | #1 / feat/foundation-ingestion | Önceki CI doğrulandı |
| Workspace | #2 / feat/career-workspace | Önceki CI doğrulandı; #1 üzerine stacked |
| Intelligence | #3 / feat/intelligence-engines | Kod d934411f; 53 Python passed / 3 skipped; browser/restore geçti. Docs head f9abc6fa CI 37381400914 ve 37381395424 başarılı |
| Retention P3a | #4 / feat/retention-maintenance | Head 2cd9f63471ac84839037df4289824ccbdc17c7a0; run 37401610008 tüm joblar başarılı. 58 Python passed / 6 skipped; restore düzeltmesi geçti |
| Scheduling P3b1 | #5 / feat/collection-scheduling | Head 360653972198dc82f43158c5040380e3174f7a69; run 37402154444 tüm joblar başarılı. 64 Python passed / 12 skipped; browser/restore geçti |
| Worker P3b2 | #6 / feat/collection-worker | Kod head 8bfe5d1b, run 37402576025 tüm joblar başarılı; 71 Python passed / 19 skipped |

PR #4 ve #5 incelemeye hazır; merge edilmedi. PR zinciri sırayla üst branch'i hedefliyor; main tamamlanmış uygulama sayılmaz.

## Aktif P3b2

Sözleşme: docs/28_COLLECTION_WORKER.md. Operator `collection-work JOB_ID`; per-source PostgreSQL session advisory lock, üç deneme sınırı, DB-clock backoff, source/schedule gate, completed ingestion'dan refetch olmadan kurtarma, orphaned RUNNING kapatma. Lock pool'a dönmeden bırakılır; bırakılamazsa connection invalidate edilir. Network exception içeriği persist edilmez. Terminal FAILED CLI exit code 1.

Kod head `8bfe5d1b4f27a57ca7e83430b5b3c12bf8665d92`; PR CI 37402576025 tüm joblar SUCCESS: Python 71 passed / 19 skipped, web, Compose/browser ve backup/restore. Sonraki commitler yalnız devam kaydı ve operator belgelerini günceller; kod kapısı doğrulandı. PR #6'nın son belge head'inin check durumunu yeniden okuyarak devam et.

Yerel Ruff/format/mypy geçti. pytest 35 passed / 55 skipped: yerelde PostgreSQL yok. Tests synthetic ve mocked HTTP kullanır. Gerçek kaynak toplama, cron/daemon kurulumu, ücretli AI çağrısı, deployment yapılmadı. HTTP exactly-once değildir: download sonrası, DB commit öncesi çökme yeniden indirmeye yol açabilir; raw revision idempotency korunur. Manual collector aynı worker lock'unu kullanmaz; reserved collection key prefix ve eşzamanlı manuel toplama yasak operasyon kuralıdır.

## Sıradaki işlemler

1. PR #6 kodu doğrulandı; son belge head CI durumunu ve review-ready bilgisini doğrula. Birleştirme yapılmadı. Sonraki aktif iş P3c ölçüm sözleşmesi ve değerlendirme aracı; bu henüz implement edilmedi.
2. P3c: docs/14 ve docs/16'daki gerçek piyasa/gold/dedupe benchmark kapısı açık. Önce annotation şeması, örneklem manifesti, ölçüm/eval aracı ve kaynak bazlı inceleme planını ayrı parça yap. Sentetik skoru gerçek piyasa başarısı diye sunma. Eski docs17 beş gözlem, temsilî veri seti veya otomatik kaynak izni değildir.
3. P4: çalıştırılabilir öğrenme alıştırmaları, başlangıç tanısı, bağımsız debugging ve İngilizce savunma rubrikleri. Mevcut çalışma alanı içerik kalitesini kanıtlamaz.
4. P5–P7: canlı model eval/bütçe, kanıta bağlı kariyer çıktıları ve gerçek hosting/TLS/offsite backup/user acceptance. Hepsi sadece secret bekleyen işler değildir.

## Doğrulama ve kurtarma

Checkout: `/workspace/scratch/0ce556516ccd/ai-career-os`. Scratch kaybolabilir; GitHub kalıcı kaynak. GitHub connector ile remote base tree → commit → expected_sha fast-forward ref kullanıldı; local commit SHA'ları farklıdır.

`uv sync --locked`; `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `uv run pytest -q`. Web: `npm ci`, lint/typecheck/build. PostgreSQL17, Compose, Playwright, hosted/Caddy config, restricted role ve backup/restore doğrulaması GitHub Actions'ta. SQLite geçişini PostgreSQL kanıtı sayma.

Retention yalnız disposable test verisinde çalıştırıldı. Maintenance DSN ayrı; PUBLIC execute revoked; runtime raw korumasını aşamaz. Kaynak retention'u derived market/plan kayıtlarını da kapsar. Yedek/offsite/export politikası ve gerçek operasyon ayrı kapıdır. Gizli anahtar veya kişisel öğrenen verisini public repo'ya koyma.

## Active P3c1 checkpoint — 2026-10-06

PR #6 final head 36f5ccf1c9b1b5903f670ffef2b56ceeac9e5376 verified: runs 37402795388 / 37402792874 SUCCESS; ready for review, not merged.
Active branch feat/market-evaluation, stacked on #6. Implemented offline exact-span mention schema/evaluator, provenance/hash/retention guards, development/holdout leakage checks, source-level metrics and synthetic fixture. See docs/29_MARKET_EVALUATION.md. Local Ruff/format/mypy pass; pytest 51 passed / 55 skipped without PostgreSQL. No real dataset or source approval, model call, merge or deployment. Next: push/open PR, verify PostgreSQL/Compose CI, record exact code head/run, then P3c2 private sampling manifest and independent review. Real market gate remains NOT_ASSESSED.

## Active overlap correction — 2026-10-06

P3c1 PR #7: https://github.com/EmreDemirelsLab/ai-career-os/pull/7. Head 9816a4a62c48afc455fb94da4c4beca0ef4bdb00; runs 37446633361 / 37446626850. Python/web passed; Compose was still running at checkpoint.
The authored evaluator fixture exposed a nested AWS/AWS Cloud duplicate. Active branch fix/mention-overlap, stacked on #7, applies policy literal-mentions/2 without changing gold. See docs30. Local Ruff/format/mypy pass; pytest 52 passed / 55 skipped. Synthetic count changes from 6 TP/1 FP/0 FN to 6 TP/0 FP/0 FN; not real-market quality. Next: push correction PR, verify both PRs' complete CI, save exact results, then P3c2 private sampling/independent review. No merge/deployment.
