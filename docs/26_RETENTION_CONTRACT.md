# P3a — retention bakım sözleşmesi

Tarih: 2026-10-06, Europe/Istanbul. Kapsam: PostgreSQL'de kaynak bazlı dry-run/apply, türetilmiş piyasa kayıtları ve geri yükleme disiplini. Gerçek veri silme bu geliştirme sırasında çalıştırılmaz.

## Kararlar

- Süre, raw revizyonunun son gözlem zamanından itibaren kaynağın `retention_days` değeridir. Tekrarlanan gerçek gözlem süreyi yeniler. Bu seçimin kaynak review kaydında kabul edilmesi gerekir; sağlayıcı farklı süre/baz isterse bu politika kullanılmaz.
- Referans zamanını veritabanı belirler. Çağıran ileride bir cutoff göndererek güncel veriyi silemez. Kaynak disabled olsa da süresi dolan veri temizlenebilir. Retention tanımı eksik kaynak hata verir; fixture kaynakları bakım kapsamı dışıdır.
- Normal API/runtime rolü raw UPDATE/DELETE yapamaz, trigger kapatamaz, bakım fonksiyonunu çalıştıramaz. Ayrı bakım rolüne yalnızca dar kapsamlı SECURITY DEFINER fonksiyonu için EXECUTE verilir; doğrudan tablo değiştirme yetkisi verilmez.
- Fonksiyon sabit güvenli search_path kullanır. Raw DELETE istisnası sadece tablo sahibinin güvenilir bakım fonksiyonu bağlamında açılır; UPDATE istisnası yoktur. Runtime'ın aynı session değişkenini ayarlaması yeterli olmaz. DB owner/superuser zaten ayrı bir güven sınırıdır.
- Dry-run silinecek raw/observation/market/plan sayılarını döndürür. Apply kilit altında yeniden hesaplar; dry-run ile apply arası yeni gözlem varsa önceki sayılara körü körüne uymaz. Transaction bütünüyle atomiktir.
- Süresi dolan raw referansı içeren market snapshot bütünüyle kaldırılır; ona bağlı adaptive plan da kaldırılır. Karma kaynaklı snapshot'ın tamamını silmek muhafazakâr bir veri azaltma tercihidir. Öğrenme gönderimleri, bağımsız kanıtlar, profil ve baseline roadmap bu işlemden etkilenmez.
- Kaynak/run istatistikleri ve içeriksiz bakım audit'i korunur. Audit sadece politika/sayı/zaman/kaynak ve operasyon anahtarı içerir; metin/span/job URL'si veya raw ID listesi içermez. Ingestion sayıları tarihsel işlem sayısıdır; kalan raw satır sayısı değildir.
- Snapshot/plan üretimi PostgreSQL advisory transaction kilidini paylaşır; bakım exclusive kilit alır. Böylece silinmiş raw metinden aynı anda yeni snapshot oluşturulması engellenir. Raw/observation silme ve ingestion yazımı tablo kilitleriyle sıralanır.
- Aynı kaynak ve apply request key tekrar çalıştırılırsa önceki sonuç döner. Yeni bakım turu yeni key gerektirir. SQLite bakım için desteklenmez; immutability testleri orada değişmez.

## Backup ve restore sınırı

Primary veriyi silmek eski dump/export/offsite kopyalarını silmez. Backup sahibi süreli saklama ve şifreleme politikası uygulamalıdır. Restore edilen DB kullanıcı trafiğine açılmadan güncel migration ve bütün gerçek kaynaklar için retention çalıştırılmalıdır. Silinmiş kaynak politikaları eski dump'ta geri gelebileceğinden, operator güncel kaynak review/retention kayıtlarını geri yüklenen DB ile uzlaştırmalıdır. Restore drill, retention uygulandıktan sonra doğrulanır. Bu parça offsite kopyaları otomatik silmez ve yasal uyum sertifikası değildir.

## Acceptance

1. Runtime rolünden raw update/delete, GUC ile bypass ve bakım çağrısı reddedilir.
2. Dry-run hiçbir satırı/audit'i değiştirmez; apply yalnız expired revizyon/observation ve bağlı market/plan kayıtlarını kaldırır.
3. Yeni gözlemi olan eski revizyon, süresi dolmamış kaynaklar ve bağımsız learner kayıtları korunur.
4. İşlem başarısızsa tüm silmeler geri alınır; replay ek silme yapmaz.
5. Tablo/temporary-object shadowing güven sınırını geçemez; izinler PUBLIC'e açık değildir.
6. Migration roundtrip, metadata drift ve restore drill disposable PostgreSQL CI'da geçer.
7. Dry-run/apply CLI, ayrı maintenance DSN ve açık apply onayı ister; web silme endpoint'i eklenmez.

Kaynak: PostgreSQL 17 [SECURITY DEFINER](https://www.postgresql.org/docs/17/sql-createfunction.html) ve [locking](https://www.postgresql.org/docs/17/explicit-locking.html), 2026-10-06 tarihinde kontrol edildi. Canlı kaynak politikası bu teknik belgelerden türetilmez.

## Operatör kullanımı

Bakım hesabı PostgreSQL'de `career_retention` rolünün üyesi olmalı; runtime hesabına üyelik verme. Hosted initializer NOLOGIN rolünü oluşturur, migration yalnız dar kapsamlı fonksiyona EXECUTE verir. Mevcut kurulumda rolü oluşturan/üyelik veren değişiklik ayrıca incelenir. Owner/superuser test amacıyla fonksiyonu çağırabilir fakat uygulama sahibi hesabı kullanmamalıdır.

```sh
# DSN secret store/environment üzerinden verilir; komuta veya PR'a yazılmaz.
career-os retention SOURCE_ID --key maintenance-cycle-001
career-os retention SOURCE_ID --key maintenance-cycle-001 \
  --apply --confirm delete-expired-source-data
```

Her iki komut `CAREER_MAINTENANCE_DATABASE_URL` ister. Dry-run çıktısındaki `*_deleted` değerleri apply edilmediyse yalnız aday sayısıdır (`applied:false`). Uygulama DSN'ine otomatik fallback yoktur. Yeni tur için yeni key; apply replay aynı kaydı döndürür. Eksik retention tanımı veya fixture kaynağı reddedilir.

`restore_drill.py` yalnız yeni disposable database'e restore eder ve fixture olmayan kaynaklarda restore sonrası retention uygular. Eski backup'ta fonksiyon/migration yoksa açık hata verir; önce izole DB'yi migrate edip kaynak politikalarını güncellemek gerekir. Bu, primary database'de bakım çalıştırmaz.

### Bilinen sınırlar

Silinen market snapshot ve ona dayanan adaptive plan yeniden görünmez; gerekirse güncel örneklemden yeni plan oluşturulur. JSON içinde manuel kopyalanmış üçüncü taraf metinler, kullanıcı indirmeleri ve başka sistemlerdeki kopyalar otomatik keşfedilmez. Kaynak kapatma süreyi iptal etmez. Bozuk türetilmiş JSON bakımın rollback yapmasına neden olabilir; sessiz kısmi silme yapılmaz. Advisory lock tek PostgreSQL DB içindir; dış servis/yedek senkronizasyonunun yerine geçmez.
