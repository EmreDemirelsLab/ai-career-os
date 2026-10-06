# Parçalı teslim ve tamamlanma planı

Güncelleme: 2026-10-06, Europe/Istanbul. Kullanıcı talimatı: işi parçalara böl; limit veya oturum değişiminde kaldığın yerden devam et. Ürün hedefi değişmedi: kişisel AI/ML öğrenme ve kariyer sistemi + production engineering portfolyosu.

## Çalışma kuralı

Her parça tek bir incelenebilir sonuç üretir: kapsam, acceptance criteria, kod/belge, test kanıtı, PR ve kalan riskler. Bir parça doğrulanmadan sonraki parça tamamlanmış sayılmaz. Yeni oturumda önce `CONTINUITY.md`, ardından buradaki aktif parçanın belgeleri ve gerçek GitHub durumu okunur. Yarım iş silinmez veya yeniden üretilmez. Kullanıcıya her parça için tekrar genel yazma izni sorulmaz. Repo'ya yazma ve PR açma yetkisi mevcut; otomatik merge/deployment yok.

| Parça | Kapsam | Kabul kriteri | Durum |
| --- | --- | --- | --- |
| P0 — Foundation | Orijinal dokümanlar, seed, v1.3 kararları, migration, ingestion/governance | İdempotency, immutable raw, failure/rejection, PostgreSQL/Compose CI | PR #1, CI doğrulandı; merge edilmedi |
| P1 — Kişisel çalışma alanı | Profil/plan sürümleri, çalışma/İngilizce, tekrar, kanıt, mülakat provası, fırsat/başvuru | Kalıcılık, export/delete, API ve tarayıcı acceptance | PR #2, CI doğrulandı; merge edilmedi |
| P2 — Intelligence ve operasyon temeli | Greenhouse adapteri, mention snapshot, önkoşullu plan, opt-in AI gateway, session, backup/restore, hosted aday | PostgreSQL yarış testleri, browser akışı, session iptali, restore, DB yetki sınırı | PR #3 kod head’i CI doğrulandı: 53 Python + 1 browser; merge edilmedi |
| P3 — Gerçek piyasa ve veri yaşam döngüsü | Kaynak bazlı review, retention/silme tasarımı, planlı toplama/recovery, gold veri, çıkarım/dedupe benchmark | Onaysız kaynağa erişim yok; expiry primary/derived/backup politikası tutarlı; gerçek örneklem ve ölçülmüş hata analizi | P3a PR #4 CI geçti; P3b1 scheduler/queue yerelde doğrulandı, PostgreSQL CI bekliyor; gerçek kaynak review/toplama yapılmadı |
| P4 — Öğrenme ve Evidence Graph kalitesi | Başlangıç tanısı, ders/alıştırma içerikleri, değerlendirme rubrikleri, bağımsız debugging ve İngilizce savunma | Her aşama için çalıştırılabilir alıştırma ve bağımsız kabul; AI yardımı ayrı; 24 hafta takvim garantisi değil | Açık; mevcut içerik çalışma iskeleti |
| P5 — Canlı AI değerlendirmesi | Seçilen model, kullanıcı onaylı kullanım sınırı, uzman-reviewed eval seti, tutor/interview kalite ölçümü | Refusal/şema/timeout yanında gerçek doğruluk, fayda, injection ve maliyet ölçümü; regresyon kapısı | Gateway var; canlı model çağrısı/kalite doğrulaması yok |
| P6 — Kariyer çıktıları | İlan gereksinimleri için kaynaklı review, ülke/rol kapsamı, başvuru paketi, proje savunması | Uydurma CV başarısı yok; her iddia kanıta bağlı; bilinmeyen uygunluk belirsiz; geri bildirim döngüsü | Manuel kayıt akışı var; tam karar/çıktı motoru açık |
| P7 — Canlıya alma ve son kabul | Seçilen sunucu/domain, TLS, monitoring, encrypted offsite backup, restore ve kullanıcı kabulü | Gerçek hedefte restart/restore/logout/erişim testleri; operasyon sahibi; açık kritik release gate yok | Hosted aday hazır; dağıtım yapılmadı |

## Sıradaki kontrollü alt parçalar

1. **P2 kapanış:** PR #3'ün güncel head'inde tüm CI job'larını doğrula; hata varsa aynı branch'te düzelt. Doğrulama kanıtını devam kaydına geçir.
2. **P3a — retention sözleşmesi:** Immutable raw veriyi sıradan API'den korurken, yalnızca yetkili bakım rolüne süreli silme sağla. Önce migration/rollback ve türetilmiş snapshot/backup etkisini tasarla; gerçek veri üzerinde silme çalıştırma. Kabul: normal runtime rolü silme korumasını aşamaz; expired/non-expired ve derived referans davranışı disposable PostgreSQL'de doğrulanır.
3. **P3b — collection orchestration:** Kaynak bazlı bounded scheduling, checkpoint/retry/recovery ve aynı verinin yeniden işlenmesini güvenli kıl. Kabul: crash sonrası yarım kayıt/çift çalışma yok; retry cap ve kaynak disable uygulanır.
4. **P3c — ölçüm:** İncelenmiş gerçek ilanlarla gold set ve karşılaştırma raporu; sentetik test puanını piyasa başarısı olarak sunma. Başlangıç hedefleri docs/16'da; erişilemeyen kaynak varsa örneklem kapsamını gerekçesiyle yeniden değerlendir.
5. P4–P7'yi aynı yöntemle küçük, doğrulanabilir alt parçalara ayır. Henüz yazılmamış kodu sadece erişim/anahtar bekliyormuş gibi göstermeme kuralı geçerlidir.

## Tamamlandı tanımı

“Bütün sistem bitti” ancak ürün sözleşmesindeki gerekli akışlar çalıştığında, gerçek veri/model kalitesi ölçüldüğünde, operasyon ve kullanıcı kabulü kapıları geçtiğinde söylenebilir. Kodun derlenmesi, mocked-provider testi veya HTTPS yapılandırması tek başına bu sonucu vermez. Kullanıcının altı ayda iş bulması/CEFR seviyesi için garanti verilmez.
