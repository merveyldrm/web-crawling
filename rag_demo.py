#!/usr/bin/env python3
"""
🚀 LangChain + ChromaDB RAG Demo
Trendyol yorum analizi için gelişmiş RAG sistemi demo'su
"""

import os
import json
from datetime import datetime
from langchain_chromadb_rag import LangChainChromaRAG

def print_separator(title: str):
    """Güzel bir ayırıcı yazdır"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print('='*60)

def demo_basic_setup():
    """Temel kurulum demo'su"""
    print_separator("TEMEL KURULUM")
    
    # RAG sistemi oluştur
    print("1. RAG sistemi oluşturuluyor...")
    rag = LangChainChromaRAG(
        persist_directory="./demo_chroma_db",
        use_openai=False,  # Ücretsiz model kullan
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # CSV kontrolü
    csv_file = "trendyol_comments.csv"
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} bulunamadı!")
        print("💡 Önce trendyol_selenium_scraper.py çalıştırın")
        return None
    
    # Yorumları yükle
    print("2. Yorumlar vector store'a yükleniyor...")
    doc_count = rag.load_comments_to_vectorstore(csv_file)
    print(f"✅ {doc_count} doküman yüklendi")
    
    return rag

def demo_external_knowledge(rag):
    """Harici bilgi ekleme demo'su"""
    print_separator("HARİCİ BİLGİ EKLEMESİ")
    
    # Örnek iş bilgileri
    business_knowledge = {
        "kargo_sla": {
            "standart_teslimat": "3-5 iş günü",
            "hızlı_teslimat": "1-2 iş günü", 
            "aynı_gün": "İstanbul, Ankara, İzmir",
            "ücretsiz_kargo": "150 TL üzeri siparişler"
        },
        "kalite_politikası": [
            "Tüm ürünler kalite kontrolünden geçer",
            "ISO 9001:2015 kalite standardına uygunluk",
            "Müşteri şikayetleri 24 saat içinde değerlendirilir",
            "Kusurlu ürünler için ücretsiz iade garantisi"
        ],
        "beden_tablosu": {
            "hassasiyet": "±1-2 cm tolerans",
            "ölçüm_standardı": "Avrupa beden standardı",
            "özel_ürünler": "Spor giyim farklı kalıpta olabilir"
        },
        "müşteri_hizmetleri": {
            "çalışma_saatleri": "7/24 online destek",
            "yanıt_süresi": "Ortalama 2 saat",
            "çözüm_oranı": "%94",
            "diller": ["Türkçe", "İngilizce", "Arapça"]
        },
        "otomatik_çözümler": {
            "kargo_gecikme": [
                "Kargo takip bilgisi SMS ile gönderilir",
                "5 günden fazla gecikmelerde otomatik tazminat",
                "Alternatif teslimat adresi seçeneği"
            ],
            "beden_uyumsuzluğu": [
                "Kolay iade prosedürü - QR kod ile",
                "Farklı beden için ücretsiz değişim",
                "Beden danışmanı chat desteği"
            ],
            "kalite_sorunu": [
                "Fotoğraf gönderimi ile hızlı değerlendirme", 
                "Kusurlu ürün için tam iade + tazminat",
                "Tedarikçi değerlendirme sürecine dahil etme"
            ]
        }
    }
    
    print("🌐 İş süreçleri bilgileri ekleniyor...")
    rag.add_external_knowledge(business_knowledge)
    print("✅ Harici bilgiler vector store'a eklendi")

def demo_similarity_search(rag):
    """Benzerlik arama demo'su"""
    print_separator("BENZERLİK ARAMA")
    
    search_queries = [
        "kargo çok geç geldi",
        "beden uymadı büyük",
        "kalite berbat bozuk",
        "müşteri hizmetleri ilgisiz"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Arama: '{query}'")
        print("-" * 40)
        
        similar_comments = rag.get_similar_comments(query, k=3)
        
        for i, comment in enumerate(similar_comments, 1):
            print(f"\n{i}. Benzer Yorum:")
            print(f"   📝 {comment['content'][:100]}...")
            metadata = comment['metadata']
            print(f"   📊 Kategori: {metadata.get('sentiment_category', 'N/A')}")
            print(f"   ⚡ Öncelik: {metadata.get('priority_score', 'N/A')}/100")

def demo_trend_analysis(rag):
    """Trend analizi demo'su"""
    print_separator("TREND ANALİZİ")
    
    trends = rag.analyze_trends()
    
    print("📊 GENEL İSTATİSTİKLER:")
    print(f"   📝 Toplam Yorum: {trends['total_comments']}")
    print(f"   📈 Ortalama Öncelik: {trends['priority_stats']['average_priority']:.1f}/100")
    print(f"   🚨 Yüksek Öncelikli: {trends['priority_stats']['high_priority_count']}")
    print(f"   📊 Kritik Oran: %{trends['priority_stats']['high_priority_percentage']}")
    
    print("\n📈 KATEGORİ DAĞILIMI:")
    for category, count in trends['category_distribution'].items():
        percentage = (count / trends['total_comments']) * 100
        print(f"   📂 {category}: {count} adet (%{percentage:.1f})")
    
    print("\n🚨 ACİL KATEGORİLER:")
    for urgent_cat, count in trends['urgent_category_distribution'].items():
        if urgent_cat != 'none':
            percentage = (count / trends['total_comments']) * 100
            print(f"   ⚠️ {urgent_cat}: {count} adet (%{percentage:.1f})")

def demo_smart_queries(rag):
    """Akıllı sorgular demo'su (LLM olmadan)"""
    print_separator("AKILLI SORGULAR (LLM SİZ)")
    
    smart_queries = [
        {
            "question": "Hangi kategoride en çok sorun var?",
            "search_terms": ["sorun", "problem", "şikayet", "memnun değilim"]
        },
        {
            "question": "Kargo ile ilgili en yaygın şikayetler neler?",
            "search_terms": ["kargo", "teslimat", "geç", "gecikme"]
        },
        {
            "question": "Kalite sorunları nasıl çözülebilir?",
            "search_terms": ["kalite", "bozuk", "defolu", "kötü"]
        }
    ]
    
    for query_info in smart_queries:
        print(f"\n❓ SORU: {query_info['question']}")
        print("-" * 50)
        
        # Her arama terimini dene
        all_results = []
        for term in query_info['search_terms']:
            results = rag.get_similar_comments(term, k=2)
            all_results.extend(results)
        
        # En yüksek öncelikli olanları al
        sorted_results = sorted(
            all_results,
            key=lambda x: x['metadata'].get('priority_score', 0),
            reverse=True
        )[:3]
        
        print("📋 BULGULAR:")
        for i, result in enumerate(sorted_results, 1):
            metadata = result['metadata']
            print(f"\n{i}. 📝 {result['content'][:150]}...")
            print(f"   ⚡ Öncelik: {metadata.get('priority_score', 0)}/100")
            print(f"   📂 Kategori: {metadata.get('sentiment_category', 'N/A')}")

def main():
    """Ana demo fonksiyonu"""
    print("🚀 LANGCHAIN + CHROMADB RAG SİSTEMİ DEMO")
    print("=" * 60)
    print("Bu demo, Trendyol yorumları için gelişmiş RAG sistemini gösterir.")
    print("LLM kullanmadan da güçlü analiz ve arama yapabilir.")
    
    try:
        # 1. Temel kurulum
        rag = demo_basic_setup()
        if rag is None:
            return
        
        # 2. Harici bilgi ekleme
        demo_external_knowledge(rag)
        
        # 3. Benzerlik arama
        demo_similarity_search(rag)
        
        # 4. Trend analizi
        demo_trend_analysis(rag)
        
        # 5. Akıllı sorgular
        demo_smart_queries(rag)
        
        print_separator("DEMO TAMAMLANDI")
        print("✅ RAG sistemi başarıyla test edildi!")
        print("\n💡 Gelişmiş özellikler için:")
        print("   - Streamlit arayüzü: streamlit run rag_chat_interface.py")
        print("   - LLM entegrasyonu: langchain_chromadb_rag.py setup_retrieval_chain()")
        print("   - API servisi: FastAPI ile web servisi kurabilirsiniz")
        
    except Exception as e:
        print(f"❌ Demo hatası: {str(e)}")
        print("\n💡 Çözüm önerileri:")
        print("   1. requirements_langchain_rag.txt paketlerini yükleyin")
        print("   2. trendyol_comments.csv dosyasının mevcut olduğunu kontrol edin")
        print("   3. ChromaDB için yeterli disk alanı olduğunu kontrol edin")

if __name__ == "__main__":
    main() 