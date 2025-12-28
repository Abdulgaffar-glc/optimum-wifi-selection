# optimum-wifi-selection
# Optimum Wi-Fi Selection System

Bu proje, **Algoritmalar dersi bitirme ödevi** kapsamında geliştirilmiş,
konum ve zaman kısıtlarını dikkate alarak en uygun Wi-Fi erişim noktasını
seçen bir **karar destek sistemidir**.

Proje, klasik “en yakın Wi-Fi” yaklaşımının yetersizliğini göstermek ve
**algoritma seçiminin sonuçlara etkisini** ortaya koymak amacıyla
tasarlanmıştır.

---

## 🎯 Problem Tanımı

Bir kullanıcının:
- bulunduğu konum,
- indirme / yükleme yapacağı dosya boyutu veya toplantı süresi,
- sahip olduğu maksimum zaman

bilgileri verilmiştir.

Amaç, kullanıcının:
> **toplam yürüyüş + işlem süresini minimize eden**
ve zaman/hız kısıtlarını sağlayan en uygun Wi-Fi ağını bulmaktır.

---

## 🧠 Kullanılan Algoritmalar ve Yöntemler

### 1️⃣ Greedy (Açgözlü) Minimizasyon Algoritması
- Her Wi-Fi noktası için toplam süre hesaplanır
- Kısıtları sağlayanlar arasından **en kısa süreli** olan seçilir
- Zaman karmaşıklığı: **O(N)**

### 2️⃣ Doğrusal Arama (Linear Search)
- Tüm Wi-Fi noktaları tek tek taranır

### 3️⃣ Kısıt Sağlama (Constraint Satisfaction)
- Maksimum süre kısıtı
- Minimum download / upload hızı kısıtları
- Uygun olmayan ağlar elenir

### 4️⃣ Manhattan Mesafe Metriği (L1 Norm)
- Kullanıcının gerçekçi yürüme mesafesini hesaplamak için kullanılmıştır
- Şehir/kampüs gibi grid yapılar için uygundur

### 5️⃣ Naive Yaklaşım (Karşılaştırma Amaçlı)
- Sadece en yakın Wi-Fi’yi seçen basit algoritma
- Geliştirilen yöntemle kıyaslama için kullanılmıştır

### 6️⃣ Sıralama (Timsort)
- Sonuç tablosu, toplam süreye göre sıralanmıştır
- `pandas.sort_values()` fonksiyonu kullanılmıştır
- Python’un yerleşik **Timsort** algoritması çalışmaktadır

---

## 🗺️ Uygulama Özellikleri

- İnteraktif harita gösterimi
- Manhattan mesafeye uygun ortogonal yol çizimi
- Farklı senaryolar:
  - Dosya indirme
  - Dosya yükleme
  - Online toplantı
- Detaylı analiz ve sıralı sonuç tablosu

---

## ⚙️ Kullanılan Teknolojiler

- Python
- Streamlit
- Pandas
- Altair

---

## ▶️ Çalıştırma

```bash
pip install streamlit pandas altair
streamlit run main.py
