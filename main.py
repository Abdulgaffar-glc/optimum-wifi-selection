import streamlit as st
import math
import random
import pandas as pd
import altair as alt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="OptimumNet", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. BÖLÜM: SABİT VERİ VE MATEMATİKSEL MODEL
# ==========================================

YURUME_HIZI_M_DK = 80  # metre/dakika
GRID_OLCEGI = 100  # 1 birim = 100 metre


class WifiNoktasi:
    def __init__(self, ad, x, y, download_mbps, upload_mbps):
        self.ad = ad
        self.x = x
        self.y = y
        self.download_mbps = download_mbps
        self.upload_mbps = upload_mbps

    def islem_suresi_hesapla(self, senaryo_tipi, miktar):
        # Bu fonksiyon "Maliyetli İşlem" simülasyonudur.
        # Eğer Greedy başarılıysa bu fonksiyonu çağırmayarak işlemci tasarrufu yapacağız.

        if senaryo_tipi == "Online Toplantı":
            if self.download_mbps < 15 or self.upload_mbps < 5:
                return float('inf')
            else:
                return miktar
        else:
            dosya_mbit = miktar * 8 * 1024
            if senaryo_tipi == "Dosya İndirme":
                if self.download_mbps <= 0: return float('inf')
                saniye = dosya_mbit / self.download_mbps
                return saniye / 60
            elif senaryo_tipi == "Dosya Yükleme":
                if self.upload_mbps <= 0: return float('inf')
                saniye = dosya_mbit / self.upload_mbps
                return saniye / 60


# --- SABİT ALTYAPI ---
if 'sabit_wifi_listesi' not in st.session_state:
    st.session_state.sabit_wifi_listesi = [
        WifiNoktasi("Merkez Kutuphane", 50, 50, 500, 100),
        WifiNoktasi("Muhendislik Lab", 30, 30, 1000, 1000),
        WifiNoktasi("Teknopark Hizli", 20, 20, 300, 300),
        WifiNoktasi("Ogrenci Isleri", 45, 55, 100, 20),
        WifiNoktasi("Spor Salonu", 10, 80, 50, 10),
        WifiNoktasi("Yurt A Blok", 80, 80, 35, 6),
        WifiNoktasi("Yurt B Blok", 85, 75, 35, 6),
        WifiNoktasi("Kafeterya Guest", 60, 40, 24, 4),
        WifiNoktasi("AVM FoodCourt", 70, 20, 50, 5),
        WifiNoktasi("Sosyal Tesisler", 25, 60, 24, 4),
        WifiNoktasi("Metro Istasyonu", 10, 10, 16, 2),
        WifiNoktasi("Park Free Wifi", 50, 10, 8, 1)
    ]

# --- SESSION STATE ---
if 'user_x' not in st.session_state: st.session_state.user_x = 15
if 'user_y' not in st.session_state: st.session_state.user_y = 15
if 'secilen_senaryo' not in st.session_state: st.session_state.secilen_senaryo = "Dosya İndirme"
if 'islem_miktari' not in st.session_state: st.session_state.islem_miktari = 20
if 'max_zaman' not in st.session_state: st.session_state.max_zaman = 60


# --- CALLBACK FONKSİYONU ---
def rastgele_senaryo_olustur():
    st.session_state.user_x = random.randint(5, 95)
    st.session_state.user_y = random.randint(5, 95)
    st.session_state.secilen_senaryo = random.choice(["Dosya İndirme", "Dosya Yükleme", "Online Toplantı"])

    if st.session_state.secilen_senaryo == "Dosya İndirme":
        st.session_state.islem_miktari = random.randint(10, 150)
        st.session_state.max_zaman = random.randint(30, 180)
    elif st.session_state.secilen_senaryo == "Dosya Yükleme":
        st.session_state.islem_miktari = random.randint(2, 20)
        st.session_state.max_zaman = random.randint(45, 240)
    else:
        st.session_state.islem_miktari = random.choice([45, 60, 90, 120])
        st.session_state.max_zaman = st.session_state.islem_miktari + random.randint(15, 60)


# ==========================================
# 2. BÖLÜM: ARAYÜZ
# ==========================================

st.title("OptimumNet: En Optimum Ağı Bul")

with st.sidebar:
    st.header("⚙️Manuel Ayarlar")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        k_x = st.number_input("X Konumu", 0, 100, key="user_x")
    with c2:
        k_y = st.number_input("Y Konumu", 0, 100, key="user_y")

    st.markdown("---")

    secilen_senaryo = st.selectbox("İşlem Tipi:", ("Dosya İndirme", "Dosya Yükleme", "Online Toplantı"),
                                   key="secilen_senaryo")

    if secilen_senaryo == "Dosya İndirme":
        etiket = "Dosya Boyutu (GB)"
        st.info("ℹ️ İndirme hızı (Download) baz alınacaktır.")
    elif secilen_senaryo == "Dosya Yükleme":
        etiket = "Yüklenecek Boyut (GB)"
        st.warning("⚠️ Yükleme hızı (Upload) baz alınacaktır.")
    else:
        etiket = "Toplantı Süresi (Dakika)"
        st.info("ℹ️ Hem Download hem Upload hızı kontrol edilecektir.")

    islem_miktari = st.number_input(etiket, min_value=1, value=st.session_state.islem_miktari)
    st.session_state.islem_miktari = islem_miktari
    max_zaman = st.slider("Maksimum Vakit (Dk)", 10, 300, key="max_zaman")

    st.markdown("---")
    st.button("🎲 RASTGELE SENARYO OLUŞTUR", on_click=rastgele_senaryo_olustur, use_container_width=True)

# ============================================================
# 3. BÖLÜM: HESAPLA BUTONU VE HİBRİT ALGORİTMA
# ============================================================
st.markdown("---")

if st.button("SİMÜLASYONU BAŞLAT (AKILLI HİBRİT MOD)", type="primary", use_container_width=True):

    # --- YARDIMCI FONKSİYON: Tam Hesaplama (Maliyetli) ---
    def veriyi_hesapla_ve_hazirla(aday_obj, durum_etiketi, renk_kodu, greedy_modu=False):
        wifi_obj = aday_obj["wifi"]
        yurume_dk = aday_obj["yurume_dk"]

        # MALİYETLİ İŞLEM: Süre hesaplama fonksiyonu çağrılıyor
        islem_dk = wifi_obj.islem_suresi_hesapla(secilen_senaryo, islem_miktari)

        toplam_dk_gosterim = 0
        islem_dk_gosterim = 0
        uygunluk = False

        if islem_dk == float('inf'):
            islem_dk_gosterim = "Hız Yetersiz"
            toplam_dk_gosterim = "Altyapı Yetersiz"
            hesaplanan_sure = float('inf')
        else:
            toplam_dk = yurume_dk + islem_dk
            islem_dk_gosterim = round(islem_dk, 1)
            toplam_dk_gosterim = round(toplam_dk, 1)
            hesaplanan_sure = toplam_dk

            if toplam_dk <= max_zaman:
                uygunluk = True
            else:
                uygunluk = False
                if greedy_modu:
                    durum_etiketi = "Süre Yetmedi"
                    renk_kodu = "#ff7f0e"  # Turuncu

        return {
            "Ağ Adı": wifi_obj.ad,
            "x": wifi_obj.x,
            "y": wifi_obj.y,
            "Download": wifi_obj.download_mbps,
            "Upload": wifi_obj.upload_mbps,
            "Uzaklık (Dk)": round(yurume_dk, 1),
            "İşlem Süresi": islem_dk_gosterim,
            "Toplam Süre": toplam_dk_gosterim,
            "Gercek_Sure_Sayisal": hesaplanan_sure,
            "Durum": durum_etiketi,
            "Renk": renk_kodu if uygunluk else "#808080",  # Gri
            "Boyut": 120 if uygunluk else 70,
            "UygunMu": uygunluk
        }


    # ============================================================
    # ADIM 1: MESAFE ÖLÇÜMÜ VE SIRALAMA
    # ============================================================
    tum_adaylar = []
    for wifi in st.session_state.sabit_wifi_listesi:
        mesafe_br = abs(wifi.x - st.session_state.user_x) + abs(wifi.y - st.session_state.user_y)
        mesafe_m = mesafe_br * GRID_OLCEGI
        yurume_dk = mesafe_m / YURUME_HIZI_M_DK
        tum_adaylar.append({"wifi": wifi, "yurume_dk": yurume_dk})

    # Mesafeye göre sırala
    tum_adaylar.sort(key=lambda x: x["yurume_dk"])

    # ============================================================
    # ADIM 2: GREEDY ARAMA (Sadece İlk 3 Aday)
    # ============================================================
    k_komsu = 3
    greedy_adaylar = tum_adaylar[:k_komsu]

    en_iyi_secenek = None
    en_kisa_sure = float('inf')
    sonuc_listesi = []
    greedy_basarili = False
    algoritma_modu = "Greedy (Sezgisel)"

    # İlk 3 adayı TAM analiz et (Maliyetli işlem)
    for aday in greedy_adaylar:
        veri = veriyi_hesapla_ve_hazirla(aday, "Aday (Greedy)", "#1f77b4", greedy_modu=True)

        if veri["UygunMu"]:
            greedy_basarili = True
            if veri["Gercek_Sure_Sayisal"] < en_kisa_sure:
                en_kisa_sure = veri["Gercek_Sure_Sayisal"]
                en_iyi_secenek = veri

        sonuc_listesi.append(veri)

    # ============================================================
    # ADIM 3: KARAR MEKANİZMASI (BUDAMA VE HESAPLAMA)
    # ============================================================

    if greedy_basarili:
        st.success("✅ **GREEDY ALGORİTMA BAŞARILI!** Optimum sonuç ilk 3 komşu içinde bulundu.")
        st.info(
            "⚡ **OPTİMİZASYON DEVREDE:** Uzaktaki ağlar için 'İşlem Süresi' hesaplaması atlandı (Pruning). İşlemci tasarrufu sağlandı.")

        # GREEDY BAŞARILIYSA: Kalanları HESAPLAMA, sadece listeye ekle ("-" bas)
        for aday in tum_adaylar[k_komsu:]:
            wifi_obj = aday["wifi"]
            sonuc_listesi.append({
                "Ağ Adı": wifi_obj.ad,
                "x": wifi_obj.x,
                "y": wifi_obj.y,
                "Download": wifi_obj.download_mbps,
                "Upload": wifi_obj.upload_mbps,
                "Uzaklık (Dk)": round(aday["yurume_dk"], 1),
                "İşlem Süresi": "-",  # HESAPLANMADI
                "Toplam Süre": "-",  # HESAPLANMADI
                "Gercek_Sure_Sayisal": float('inf'),  # Sıralamada en sona gitmesi için
                "Durum": "Hesaplanmadı (Optimizasyon)",
                "Renk": "#d3d3d3",  # Açık Gri
                "Boyut": 50,
                "UygunMu": False
            })

    else:
        st.warning(
            "⚠️ **GREEDY YETERSİZ KALDI!** Yakındaki ağlar kriterleri sağlamıyor. **BRUTE-FORCE** moduna geçiliyor...")
        algoritma_modu = "Brute-Force (Kapsamlı)"

        # GREEDY BAŞARISIZSA: Kalanları HESAPLA (Maliyetli işlem yap)
        for aday in tum_adaylar[k_komsu:]:
            veri = veriyi_hesapla_ve_hazirla(aday, "Uzak Alternatif", "#1f77b4", greedy_modu=False)

            if veri["UygunMu"]:
                veri["Durum"] = "Alternatif (Uzak)"
                if veri["Gercek_Sure_Sayisal"] < en_kisa_sure:
                    en_kisa_sure = veri["Gercek_Sure_Sayisal"]
                    en_iyi_secenek = veri
            else:
                if veri["Toplam Süre"] == "Altyapı Yetersiz":
                    veri["Durum"] = "Hız Yetersiz"
                else:
                    veri["Durum"] = "Süre Yetmiyor"

            sonuc_listesi.append(veri)

    # ============================================================
    # ADIM 4: GÖRSELLEŞTİRME
    # ============================================================

    # En iyi seçeneği yeşil yap
    if en_iyi_secenek:
        for veri in sonuc_listesi:
            if veri["Ağ Adı"] == en_iyi_secenek["Ağ Adı"]:
                veri["Durum"] = "✅ EN UYGUN"
                veri["Renk"] = "#2ca02c"
                veri["Boyut"] = 400
                break

    # Kullanıcıyı Haritaya Ekle
    sonuc_listesi.append({
        "Ağ Adı": "📍 SİZİN KONUMUNUZ", "x": st.session_state.user_x, "y": st.session_state.user_y,
        "Download": 0, "Upload": 0, "Uzaklık (Dk)": 0, "İşlem Süresi": "-", "Toplam Süre": "-",
        "Gercek_Sure_Sayisal": 0, "Durum": "Kullanıcı", "Renk": "#d62728", "Boyut": 300
    })

    # --- Grafik Çizimi ---
    df_tum_noktalar = pd.DataFrame(sonuc_listesi)

    yol_verisi = []
    if en_iyi_secenek:
        yol_verisi.append({
            "x_basla": st.session_state.user_x, "y_basla": st.session_state.user_y,
            "x_bitis": en_iyi_secenek["x"], "y_bitis": st.session_state.user_y,
            "Renk": "#2ca02c"
        })
        yol_verisi.append({
            "x_basla": en_iyi_secenek["x"], "y_basla": st.session_state.user_y,
            "x_bitis": en_iyi_secenek["x"], "y_bitis": en_iyi_secenek["y"],
            "Renk": "#2ca02c"
        })

    df_yollar = pd.DataFrame(yol_verisi)

    col_map, col_analysis = st.columns([3, 1])

    with col_map:
        st.subheader(f"🗺️ Algoritma Modu: {algoritma_modu}")

        base = alt.Chart(df_tum_noktalar).encode(x=alt.X('x', title='X Konumu'), y=alt.Y('y', title='Y Konumu'))

        points = base.mark_circle().encode(
            color=alt.Color('Renk', scale=None),
            size=alt.Size('Boyut', legend=None),
            tooltip=['Ağ Adı', 'Durum', 'Toplam Süre', 'Uzaklık (Dk)', 'Download']
        )

        text = base.mark_text(dy=-15, color='white').encode(text='Ağ Adı')

        if not df_yollar.empty:
            lines = alt.Chart(df_yollar).mark_rule().encode(
                x='x_basla', y='y_basla', x2='x_bitis', y2='y_bitis',
                color=alt.Color('Renk', scale=None), strokeWidth=alt.value(4)
            )
            chart = (lines + points + text).interactive()
        else:
            chart = (points + text).interactive()

        st.altair_chart(chart, use_container_width=True)

    with col_analysis:
        st.subheader("📊 Sonuç Analizi")
        if en_iyi_secenek:
            st.success(f"**Seçilen Ağ:**\n{en_iyi_secenek['Ağ Adı']}")
            st.metric("Toplam Süre", f"{en_iyi_secenek['Toplam Süre']} dk")
            if isinstance(en_iyi_secenek['Gercek_Sure_Sayisal'], (int, float)):
                st.metric("Tasarruf", f"{round(max_zaman - en_iyi_secenek['Gercek_Sure_Sayisal'], 1)} dk")
        else:
            st.error("Hiçbir ağ kriterleri sağlamadı!")

    # --- Tablo Gösterimi ---
    gosterilecek_sutunlar = ['Ağ Adı', 'Durum', 'Toplam Süre', 'Uzaklık (Dk)', 'Download', 'Upload']

    # Sıralama mantığı: Sayıları sırala, "-" veya metin olanları en sona at
    st.dataframe(
        df_tum_noktalar[gosterilecek_sutunlar].sort_values(
            by="Toplam Süre",
            key=lambda x: pd.to_numeric(x, errors='coerce').fillna(99999)
        ),
        use_container_width=True
    )

else:
    st.info("Algoritmayı çalıştırmak için butona basın.")