from advanced_comment_analyzer import AdvancedCommentAnalyzer
from comment_summarizer import CommentSummarizer

def main():
    print("🚀 GELİŞMİŞ YORUM ANALİZ SİSTEMİ")
    print("="*50)
    
    # Gelişmiş analizci ve mevcut özetleyici
    advanced_analyzer = AdvancedCommentAnalyzer()
    basic_summarizer = CommentSummarizer()
    
    # Yorumları yükle
    comments = advanced_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if not comments:
        print("Yorum yüklenemedi!")
        return
    
    print(f"📊 {len(comments)} yorum yüklendi")
    
    # 1. GELİŞMİŞ KATEGORİ BAZLI ANALİZ
    print("\n🔍 1. Gelişmiş kategori bazlı analiz başlıyor...")
    analysis_results = advanced_analyzer.analyze_all_comments(comments)
    
    # Kategori raporunu göster
    category_report = advanced_analyzer.generate_category_report(analysis_results)
    print(category_report)
    
    # 2. GELENEKSEL AI ÖZET
    print("\n🤖 2. AI destekli genel özet oluşturuluyor...")
    textile_keywords = ['beden', 'kalıp', 'giyim', 'elbise', 'pantolon', 'gömlek', 'etek', 'ceket']
    all_comment_text = " ".join([comment.get('comment', '').lower() for comment in comments])
    include_beden_renk = any(keyword in all_comment_text for keyword in textile_keywords)
    
    ai_summary = basic_summarizer.generate_ai_summary(comments, include_beden_renk=include_beden_renk)
    
    # 3. DOSYALARI KAYDET
    print("\n💾 3. Raporlar kaydediliyor...")
    
    # Detaylı JSON analizi
    advanced_analyzer.save_detailed_analysis(analysis_results, 'detailed_analysis.json')
    
    # AI özeti
    basic_summarizer.save_ai_summary_to_txt(ai_summary, 'ai_summary.txt')
    
    # Kategori bazlı filtrelenmiş raporlar
    categories_to_export = ['kargo', 'kalite', 'fiyat', 'musteri_hizmeti']
    
    for category in categories_to_export:
        # Negatif yorumlar
        negative_comments = advanced_analyzer.filter_comments_by_category_sentiment(
            analysis_results, category, 'negative'
        )
        if negative_comments:
            advanced_analyzer.save_filtered_report(
                analysis_results, category, 'negative', 
                f'{category}_sikayetler.txt'
            )
        
        # Pozitif yorumlar  
        positive_comments = advanced_analyzer.filter_comments_by_category_sentiment(
            analysis_results, category, 'positive'
        )
        if positive_comments:
            advanced_analyzer.save_filtered_report(
                analysis_results, category, 'positive',
                f'{category}_ovguler.txt'
            )
    
    # 4. İNTERAKTİF MENÜ
    print("\n" + "="*60)
    print("✅ ANALİZ TAMAMLANDI!")
    print("="*60)
    
    while True:
        print("\n🔍 Hangi kategoriye odaklanmak istiyorsunuz?")
        print("1. Kargo şikayetleri")
        print("2. Kalite övgüleri") 
        print("3. Fiyat yorumları (tümü)")
        print("4. Müşteri hizmeti sorunları")
        print("5. Ürün özellikleri (pozitif)")
        print("6. Beden/uyum sorunları (giyim için)")
        print("7. Detaylı JSON dosyasını göster")
        print("8. Çıkış")
        
        choice = input("\nSeçiminiz (1-8): ").strip()
        
        if choice == '1':
            show_filtered_comments(analysis_results, advanced_analyzer, 'kargo', 'negative')
        elif choice == '2':
            show_filtered_comments(analysis_results, advanced_analyzer, 'kalite', 'positive')
        elif choice == '3':
            show_filtered_comments(analysis_results, advanced_analyzer, 'fiyat')
        elif choice == '4':
            show_filtered_comments(analysis_results, advanced_analyzer, 'musteri_hizmeti', 'negative')
        elif choice == '5':
            show_filtered_comments(analysis_results, advanced_analyzer, 'urun_ozellikleri', 'positive')
        elif choice == '6':
            show_filtered_comments(analysis_results, advanced_analyzer, 'beden_uyum', 'negative')
        elif choice == '7':
            print("\n📄 Detaylı JSON analizi 'detailed_analysis.json' dosyasında kaydedildi.")
            print("Bu dosyada tüm kategoriler, sentiment skorları ve filtreleme seçenekleri bulunur.")
        elif choice == '8':
            print("👋 Sistem kapatılıyor...")
            break
        else:
            print("❌ Geçersiz seçim! Lütfen 1-8 arası bir sayı girin.")

def show_filtered_comments(analysis_results, analyzer, category, sentiment=None):
    """Filtrelenmiş yorumları göster"""
    comments = analyzer.filter_comments_by_category_sentiment(analysis_results, category, sentiment)
    
    if not comments:
        print(f"\n❌ {category} kategorisinde {sentiment or 'herhangi bir'} sentiment'te yorum bulunamadı.")
        return
    
    sentiment_text = f" ({sentiment})" if sentiment else ""
    print(f"\n📋 {category.upper()}{sentiment_text} - Toplam: {len(comments)} yorum")
    print("="*60)
    
    # İlk 5 yorumu göster
    for i, comment in enumerate(comments[:5], 1):
        print(f"\n{i}. YORUM:")
        print(f"   👤 Kullanıcı: {comment['user']}")
        print(f"   📅 Tarih: {comment['date']}")
        print(f"   💬 Yorum: {comment['comment'][:200]}...")
        if 'analysis' in comment and comment['analysis']['keywords_found']:
            print(f"   🔍 Anahtar Kelimeler: {', '.join(comment['analysis']['keywords_found'])}")
    
    if len(comments) > 5:
        print(f"\n... ve {len(comments) - 5} yorum daha.")
        print(f"Tüm yorumları görmek için '{category}_{sentiment}_comments.txt' dosyasını kontrol edin.")

if __name__ == "__main__":
    main() 