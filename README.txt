# VYNE - Vulnerability Yielding Network Enumerator v1.0
		   (Zafiyet Ortaya Çıkaran Ağ Tarayıcı)

VYNE, hedef sistemler üzerinde subdomain ve endpoint keşfi yapabilen, wildcard kontrolü içeren, GET ve POST isteklerini destekleyen çok amaçlı bir güvenlik tarama aracıdır.

## Özellikler

- Subdomain taraması (wordlist destekli)
- Wildcard subdomain tespiti
- Endpoint (URL path) taraması
- GET ve POST HTTP metodları desteği
- POST için key-value veya data formatında wordlist kullanımı
- HTTP durum kodlarına göre filtreleme imkanı
- JSON formatında çıktı üretimi
- Çoklu iş parçacığı (thread) ile hızlı tarama

## Kurulum

```bash
git clone https://github.com/Sh4d0wHunt3r-XD/VYNE-v1.0.git
cd VYNE
pip3 install -r requirements.txt
Python 3.6 ve üzeri önerilir.


KULLANIM ÖRNEKLERİ:

Temel kullanım örneği:
python3 vyne.py -u https://example.com -w wordlist.txt

Subdomain ve endpoint taraması birlikte:
python3 vyne.py -u https://example.com -w endpoints.txt -s subdomains.txt

Sadece subdomain taraması:
python3 vyne.py -u https://example.com -s subdomains.txt --noendpoint

POST isteği ile brute force:
python3 vyne.py -u https://example.com/login -X POST -K keys.txt -V values.txt

Sonuçları JSON dosyasına kaydetme:
python3 vyne.py -u https://example.com -w wordlist.txt -o /path/to/output/

HTTP durum kodlarına göre filtreleme:
python3 vyne.py -u https://example.com -w wordlist.txt --status 200,403

| Parametre         | Açıklama                                                            |
| ----------------- | ------------------------------------------------------------------- |
| -u, --url         | Hedef URL (zorunlu)                                                 |
| -w, --wordlist    | Endpoint taraması için wordlist dosyası                             |
| -s, --subwordlist | Subdomain taraması için wordlist dosyası                            |
| -X, --method      | HTTP metodu (GET veya POST), varsayılan GET                         |
| -K, --keys        | POST isteği için key wordlist dosyası                               |
| -V, --values      | POST isteği için value wordlist dosyası                             |
| -D, --datas       | POST isteği için key=value\&key2=value2 formatında wordlist dosyası |
| -t, --thread      | İş parçacığı (thread) sayısı, varsayılan 5                          |
| --timeout         | HTTP isteği zaman aşımı süresi (saniye), varsayılan 15              |
| -o, --output      | Çıktıların kaydedileceği dizin                                      |
| --status          | Filtrelenecek HTTP durum kodları (virgülle ayrılmış)                |
| -fs, --firstsub   | Önce subdomain taraması yapılacak                                   |
| --noendpoint      | Endpoint taraması yapılmayacak                                      |
| -U, --user-agent  | HTTP isteği için User-Agent belirtebilirsiniz                       |


ÇIKTI:
Tarama sonuçları JSON formatında belirtilen dizine kaydedilir. Örnek:

[
  {
    "url": "https://admin.example.com",
    "status": 200
  },
  {
    "url": "https://example.com/login",
    "status": 302,
    "redirect": "https://example.com/dashboard"
  }
]

| Özellik / Araç     | VYNE | ffuf | Amass | Dirsearch | Sublist3r |
| ------------------ | :--: | :--: | :---: | :-------: | :-------: |
| Subdomain Taraması |   ✔  |   ✘  |   ✔   |     ✘     |     ✔     |
| Wildcard Kontrolü  |   ✔  |   ✘  |   ⚠️  |     ✘     |     ✘     |
| Endpoint Taraması  |   ✔  |   ✔  |   ✘   |     ✔     |     ✘     |
| POST Desteği       |   ✔  |  ⚠️  |   ✘   |     ✘     |     ✘     |
| JSON Çıktı         |   ✔  |   ✔  |   ✔   |     ✔     |     ✘     |


*✔: Var, ✘: Yok, ⚠️: Kısıtlı/Dolaylı destek

Lisans:
MIT Lisansı altında yayınlanmaktadır.


UYARI:
Bu araç yalnızca yasal ve yetkili güvenlik testleri için kullanılmalıdır. Yasadışı veya yetkisiz kullanımların sorumluluğu kullanıcıya aittir.
