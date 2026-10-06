# AI Career OS — devam kaydı

2026-10-06, Europe/Istanbul. Kullanıcı sistemi parçalara bölerek tamamlamamızı, test/PR kanıtlarını ve kaldığımız yeri korumamızı istedi. Repo yazımı/PR açma yetkili; otomatik merge/deployment yok. Üretilen kod kullanıcının bağımsız beceri kanıtı değildir.

## Devam ederken

Önce AGENTS.md, docs/25_DELIVERY_PLAN.md, docs/29_MARKET_EVALUATION.md ve docs/30_MENTION_POLICY_V2.md oku. Remote head/CI durumunu doğrula. Güncel aktif iş için dosyanın son checkpoint bölümünü oku; eski bölümler tarihçedir.

## Doğrulanmış teslimler

Repo: https://github.com/EmreDemirelsLab/ai-career-os. PR zinciri önceki feature branch üzerine stacked; main tamamlanmış uygulama değildir. Merge yapılmadı.

| Parça | PR / branch | Kanıt |
| --- | --- | --- |
| Foundation | #1 / feat/foundation-ingestion | Önceki CI doğrulandı |
| Workspace | #2 / feat/career-workspace | Önceki CI doğrulandı |
| Intelligence | #3 / feat/intelligence-engines | Kod d934411f: 53 Python passed / 3 skipped; browser/restore geçti. Docs f9abc6fa CI 37381400914/37381395424 başarılı |
| Retention | #4 / feat/retention-maintenance | Head 2cd9f634; run 37401610008 başarılı; 58 passed / 6 skipped |
| Scheduling | #5 / feat/collection-scheduling | Head 36065397; run 37402154444 başarılı; 64 passed / 12 skipped |
| Worker/recovery | #6 / feat/collection-worker | Final head 36f5ccf1c9b1b5903f670ffef2b56ceeac9e5376; runs 37402795388/37402792874 başarılı; kodda 71 passed / 19 skipped |
| Offline evaluation | #7 / feat/market-evaluation | Head 9816a4a62c48afc455fb94da4c4beca0ef4bdb00; run 37446633361 tüm joblar başarılı; 87 passed / 19 skipped |
| Mention overlap fix | #8 / fix/mention-overlap | Kod head 502a36641aea51a097dc4baac7ff09f85d81c04d; run 37446823448 tüm joblar başarılı; 88 passed / 19 skipped |

PR #7/#8 Python, web, Compose/browser ve backup/restore kontrolleri geçti. Son checkpoint commit'i yalnız belgeleri günceller; son belge head CI durumunu yeniden kontrol et. Ready-for-review durumunu PR'dan oku; merge varsayma.

## Son parçada uygulananlar

`market_eval.py`: çevrimdışı Pydantic annotation şeması; tam metin hash'i, taxonomy/span/expiry kontrolleri; development/holdout group ve normalize exact-text leakage reddi; overall/per-source TP/FP/FN, precision/recall/F1; tanımsız oranlar null; bounded dosya okuma ve redacted CLI. Kaynak metni raporda yok. Reviewer alanı gerçek insan incelemesini kanıtlamaz. Her rapor market_release_gate=NOT_ASSESSED.

Authored synthetic fixture gerçek piyasa verisi değildir. AWS Cloud örneği v1 extractor'da iç içe AWS/AWS Cloud tekrarını ortaya çıkardı. Ayrı PR #8, gold'u değiştirmeden literal-mentions/2 politikasıyla aynı canonical skill'in maximal span'ını tutuyor; ayrı tekrarlar korunuyor. Yedi sentetik örnekte 6 TP/1 FP/0 FN → 6 TP/0 FP/0 FN. Bu test incelenerek düzeltildi; bağımsız gerçek-market kalite ölçümü değildir. Eski persisted snapshot'lar yeniden yazılmaz.

Yerel Ruff/format/mypy geçti; son pytest 52 passed / 55 skipped (PostgreSQL yerelde yok). CLI smoke geçti. Gerçek kaynak toplama, cron/daemon, ücretli model çağrısı veya deployment yapılmadı.

## Sıradaki kontrollü iş

1. PR #8'in son belge head CI'sını doğrula. Hata varsa aynı branch'te düzelt; yeni kod yazmadan mevcut checkpoint'i oku.
2. P3c2: private sampling manifest/schema; Germany/other EU/outside/unknown, role, seniority, company/source, language ve remote restriction katmanları; gözlem tarihi, exclusion reason ve missingness. Exact-source policy review kaydı olmadan otomatik toplama yok. docs17'nin beş tarihi gözlemi corpus veya otomatik izin değildir.
3. Private gerçek örneklem, bağımsız insan etiketlemesi ve disagreement review; leakage-group bazlı frozen split. docs16'daki 500–1,000 corpus / 100+ extraction example hedefleri açık. Dedupe pair/cluster ve semantic requirement/eligibility ölçümleri ayrıca tasarlanmalı. Threshold'ları gerçek baseline ölçümünden önce ilan et; sentetik puanı pazar başarısı diye sunma.
4. P4: çalıştırılabilir ders/alıştırma, tanı, bağımsız debugging ve İngilizce savunma rubrikleri. P5: canlı model eval/bütçe. P6: kanıta bağlı kariyer çıktıları. P7: gerçek hosting/TLS/monitoring/offsite backup/user acceptance. Bunların tamamı yalnız secret bekleyen işler değildir. Tam ürün bitti deme.

## Operasyon ve kurtarma

Checkout `/workspace/scratch/0ce556516ccd/ai-career-os`; GitHub kalıcı kaynak. Connector ile remote base tree → commit → expected_sha fast-forward ref kullanıldı; local commit SHA'ları farklıdır. Local history'yi force-push etme. Scratch kaybolursa remote branch'ten kurtar.

`uv sync --locked`; `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `uv run pytest -q`. Evaluation: `uv run python -m career_os.market_eval tests/evals/mentions_synthetic_v1.json --split holdout --as-of 2026-10-06`. Web lint/typecheck/build ve PostgreSQL17/Compose/Playwright/Caddy/restricted-role/restore CI'da doğrulanır; SQLite kanıtı eşdeğer değildir.

Retention yalnız disposable fixture'larda çalıştırıldı. Maintenance DSN ayrı; gerçek veriye bakım uygulama. Real evaluation dosyaları public repo dışında/ignored evaluation-private altında ve kaynak retention'una tabi; ignore erişim kontrolü değildir. Eval expiry reddeder ama dosya/backup silmez. Gizli anahtarları ve kişisel verileri repo'ya koyma.

Worker kaynak başına DB session lock, en fazla üç deneme ve crash recovery kullanır. HTTP exactly-once değildir; manual collector aynı lock'u kullanmaz. Reserved collection key prefix ve eşzamanlı manuel toplama yasağı operator kuralıdır. Bkz. docs28.

## Active P3c2 checkpoint — 2026-10-06

User explicitly clarified: do not stop after a PR; continue implementing successive parts until an actual limit/blocker, recording checkpoints.
PR #8 final head 8255f7c408ecc287df7ed4492634b38322b13997 CI 37447289524/37447283848 both SUCCESS. Active branch feat/sampling-review, stacked on #8. sampling.py and docs31 implement private manifest, strata/missingness, policy/retention, independent-token review and stale-gold linkage checks. Synthetic fixtures only. Local Ruff/format/mypy pass; pytest 64 passed / 55 skipped. Next: push PR and verify CI; then proceed to P4 diagnostic/exercise content while real market collection/independent human review stays explicitly open. No live collection/paid calls/merge/deployment.

## Active P4a checkpoint — 2026-10-06

P3c2 PR #9 head 49d6acc278118477a95eee2641269b4acee6579e: runs 37456402632/37456397956 both SUCCESS; Python 100 passed / 19 skipped. Ready for review, not merged.
Active branch feat/foundation-lessons, stacked on #9. Four authored week1–4 lessons, objective checks separate from mastery, local starter/reference/check runner, authenticated lesson API using LearningAttempt recall/export/delete, and web tab plus browser acceptance implemented. See docs32 and labs/foundation/README.md. Local Python 66 passed / 56 skipped; Ruff/mypy and web lint/type/build passed; reference five checks passed, starter intentionally fails. Next: push PR and verify final CI including new browser flow; fix any failures. Then continue P4 content/diagnosis, not stop after PR. Real-market corpus/independent review and full-course validation remain open.

## Active P4b checkpoint — 2026-10-06

P4a PR #10 head 470d6159c11c8eb74d3de7c68d22f968a6c51beb: runs 37457433007/37457427281 all SUCCESS; Python 103 passed / 19 skipped, new browser lesson/save/reload/export and restore passed. Ready for review, not merged.
Active branch feat/data-ml-lessons, stacked on #10. Catalog foundation-lessons/2 adds weeks5–8; labs/data_ml starter/reference/check runner; optional pandas labs dependency group plus uv.lock and CI setup. Local Ruff/mypy passed, pytest 67 passed / 56 skipped using --group labs. Reference five checks passed. A mistaken test-only recall count edit was fixed; per-attempt recall remains four intervals. Next: push PR, verify CI, then implement formative next-practice suggestions without mastery claims. Continue after PR, do not stop routinely. Standard full test command now uv run --group labs pytest -q.

## Integrated workflow checkpoint — 2026-10-06

PR #11 head 559319823b71ffa88a373e9cbff33b33486e4c7c: CI 37458201238 Python/web/Compose/browser/restore SUCCESS; 104 passed / 19 skipped. Ready for review, unmerged.
Active branch feat/next-practice extends #11. Deterministic next-practice suggestions, latest attempt per lesson beyond the history window, multi-requirement opportunity form, downloadable evidence-linked career preparation, and expanded browser learning/evidence/interview/opportunity/application flow. Local Python 71 passed / 58 skipped; Ruff/mypy and web lint/typecheck/build passed. Remote CI pending. See docs34.
Next: verify remote CI on this exact code, fix failures, then continue remaining authored learning content and product acceptance. Do not stop routinely after creating a PR. No merge/deploy, live collection or paid AI calls performed. Full course validation, real market benchmarks, live AI evaluation and actual hosting acceptance remain open.

## 24-week coverage and browser fixes — active, 2026-10-06

PR #12 feat/next-practice first head 66e845cb786c1564a2748a71cce190e747ee917c had green Python/web but browser failure: global aside style overlaid lesson controls. Head a52fbe68cc4b943bd656226ace5990a49d04f6fd fixes scoped sidebar CSS; its browser test then found ambiguous multi-select labels. Explicit labels fixed locally; do not mark acceptance until new CI passes.
Same branch now includes catalog v3, all 24 authored weekly units, 16 offline applied-AI labs with starter/reference/checks, direct plan-to-lesson navigation and docs35. Local Python 72 passed / 58 skipped; reference 16 checks passed and all untouched starters fail. These are small engineering boundary exercises, not full framework/model competency or independently validated course. Next: push combined changes to PR12, verify full CI, fix remaining browser failures, record exact final head/run.
