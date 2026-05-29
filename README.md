# İkili Çarpma Turing Makinesi

Bu proje, bilgisayar bilimlerinin en temel kavramlarından biri olan Turing makinelerini pratikte gözlemleyebilmeniz için geliştirilmiştir. Proje kapsamında, iki adet ikili (binary) sayıyı birbirleriyle çarpan özel bir Turing makinesi tasarımı yer almaktadır.

---

## Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda kurup çalıştırmak için aşağıdaki adımları takip edebilirsiniz.

### Gereksinimler

Uygulamanın çalışması için bilgisayarınızda Python 3.9 veya daha güncel bir sürümün kurulu olması önerilir.

### Adım Adım Kurulum

1. Proje dizinine terminal üzerinden geçiş yapın:
   ```bash
   cd Binary-Multiplication
   ```

2. Proje bağımlılıklarının izole kalması için sanal bir ortam (virtual environment) oluşturup aktifleştirmenizi tavsiye ederiz:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

### Çalıştırma

Kurulumu tamamladıktan sonra simülasyonu başlatmak için şu komutu çalıştırmanız yeterlidir:

```bash
python3 main.py
```

---

## Projedeki Turing Makinesi: İkili Çarpıcı (Binary Multiplier)

Bu projede yer alan temel yapı, iki ikili sayının çarpımını gerçekleştiren İkili Çarpıcı makinesidir.

### Çalışma Mantığı ve Girdi Biçimi

Makine, tek bir şerit (tape) üzerinde çalışır ve girdi olarak belirli bir şablonu bekler:
- Girdi biçimi `<a>*<b>=` şeklinde olmalıdır (örneğin: `101*11=`).
- Bu örnekte `101` birinci sayıyı (ondalık karşılığı 5), `*` çarpma işaretini, `11` ikinci sayıyı (ondalık karşılığı 3) ve `=` ise hesaplamanın başlayacağı sınırı temsil eder.

### Uygulanan Algoritma

Makine, çarpma işlemini gerçekleştirmek için klasik "Kaydır ve Ekle" (Shift and Add) algoritmasını simüle eder:
- İkinci sayının her bir bitini sırayla kontrol eder.
- Eğer ilgili bit `1` ise, birinci sayıyı şeridin sonundaki sonuç bölümüne ekler.
- Her adımdan sonra sayıları şerit üzerinde kaydırarak hizalamayı sağlar.
- İşlem tamamlandığında, sonucu şerit üzerine ikili sistemde (en önemsiz bit - LSB ilk sırada olacak şekilde) yazar ve makine başarıyla durduğunda ondalık tabandaki karşılığını da hesaplayarak sunar.
