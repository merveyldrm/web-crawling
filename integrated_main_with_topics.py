from advanced_comment_analyzer import AdvancedCommentAnalyzer
from comment_summarizer import CommentSummarizer
from topic_modeling_analyzer import TopicModelingAnalyzer

def main():
    print("🚀 GELİŞMİŞ YORUM ANALİZ SİSTEMİ v2.0")
    print("📊 Sentiment + Kategori + Konu Çıkarımı")
    print("="*60)
    
    # Analizcileri başlat
    advanced_analyzer = AdvancedCommentAnalyzer()
    basic_summarizer = CommentSummarizer()
    topic_analyzer = TopicModelingAnalyzer()
    
    # Yorumları yükle
    comments = advanced_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if not comments:
        print("❌ Yorum yüklenemedi!")
        return
    
    print(f"📊 {len(comments)} yorum yüklendi")
    
    # Kullanıcı seçimi
    print("\n🔍 Hangi analiz türünü istiyorsunuz?")
    print("1. 🎭 Sentiment + Kategori Analizi (Hızlı)")
    print("2. 🧠 Otomatik Konu Çıkarımı (LDA + Clustering)")
    print("3. 🚀 Tüm Analizler (Kapsamlı)")
    print("4. 📋 Sadece Konu Modelleme")
    
    choice = input("\nSeçiminiz (1-4): ").strip()
    
    if choice in ['1', '3']:
        # 1. SENTIMENT + KATEGORİ ANALİZİ
        print("\n🎭 1. Sentiment + Kategori analizi başlıyor...")
        analysis_results = advanced_analyzer.analyze_all_comments(comments)
        
        category_report = advanced_analyzer.generate_category_report(analysis_results)
        print(category_report)
        
        # Dosyaları kaydet
        advanced_analyzer.save_detailed_analysis(analysis_results, 'sentiment_analysis.json')
    
    if choice in ['2', '3', '4']:
        # 2. KONU ÇIKARIMİ ANALİZİ
        print("\n🧠 2. Otomatik konu çıkarımı başlıyor...")
        
        if len(comments) < 10:
            print("⚠️ Konu analizi için en az 10 yorum gerekli!")
        else:
            topic_results = topic_analyzer.analyze_topics(comments, lda_topics=5, cluster_topics=5)
            
            if 'error' not in topic_results:
                topic_report = topic_analyzer.generate_topic_report(topic_results)
                print(topic_report)
                
                # Konu analizi dosyalarını kaydet
                topic_analyzer.save_topic_analysis(topic_results, 'topic_analysis.json')
                topic_analyzer.save_topic_report(topic_results, 'topic_report.txt')
            else:
                print(f"❌ Konu analizi hatası: {topic_results['error']}")
    
    if choice == '3':
        # 3. GELENEKSEl AI ÖZET
        print("\n🤖 3. AI destekli genel özet oluşturuluyor...")
        textile_keywords = ['beden', 'kalıp', 'giyim', 'elbise', 'pantolon']
        all_comment_text = " ".join([comment.get('comment', '').lower() for comment in comments])
        include_beden_renk = any(keyword in all_comment_text for keyword in textile_keywords)
        
        ai_summary = basic_summarizer.generate_ai_summary(comments, include_beden_renk=include_beden_renk)
        basic_summarizer.save_ai_summary_to_txt(ai_summary, 'ai_summary.txt')
    
    # 4. İNTERAKTİF MENÜ
    if choice in ['1', '3']:
        print("\n" + "="*60)
        print("✅ ANALİZ TAMAMLANDI!")
        print("="*60)
        
        while True:
            print("\n🔍 Hangi detayı incelemek istiyorsunız?")
            print("1. 🚚 Kargo şikayetleri")
            print("2. ⭐ Kalite övgüleri") 
            print("3. 💰 Fiyat yorumları")
            print("4. 🎧 Müşteri hizmeti sorunları")
            print("5. 📊 Ürün özellikleri (pozitif)")
            print("6. 👔 Beden/uyum sorunları")
            print("7. 📄 Konu analizi sonuçları")
            print("8. 📁 Dosya listesi")
            print("9. 🚪 Çıkış")
            
            sub_choice = input("\nSeçiminiz (1-9): ").strip()
            
            if sub_choice == '1':
                show_filtered_comments(analysis_results, advanced_analyzer, 'kargo', 'negative')
            elif sub_choice == '2':
                show_filtered_comments(analysis_results, advanced_analyzer, 'kalite', 'positive')
            elif sub_choice == '3':
                show_filtered_comments(analysis_results, advanced_analyzer, 'fiyat')
            elif sub_choice == '4':
                show_filtered_comments(analysis_results, advanced_analyzer, 'musteri_hizmeti', 'negative')
            elif sub_choice == '5':
                show_filtered_comments(analysis_results, advanced_analyzer, 'urun_ozellikleri', 'positive')
            elif sub_choice == '6':
                show_filtered_comments(analysis_results, advanced_analyzer, 'beden_uyum', 'negative')
            elif sub_choice == '7':
                if 'topic_results' in locals():
                    print("\n📊 KONU ANALİZİ ÖZETİ:")
                    print("-" * 40)
                    
                    # LDA konularını göster
                    if 'lda_analysis' in topic_results and 'topics' in topic_results['lda_analysis']:
                        print("\n🤖 LDA Konuları:")
                        for topic in topic_results['lda_analysis']['topics']:
                            print(f"   📋 {topic['topic_name']}: {', '.join(topic['words'][:3])}")
                    
                    # Clustering sonuçlarını göster
                    if 'clustering_analysis' in topic_results and 'clusters' in topic_results['clustering_analysis']:
                        print("\n🧠 Clustering Konuları:")
                        for cluster in topic_results['clustering_analysis']['clusters']:
                            percentage = round(cluster['size'] / topic_results['clustering_analysis']['model_info']['total_documents'] * 100, 1)
                            print(f"   📊 {cluster['topic_name']}: %{percentage} ({cluster['size']} yorum)")
                else:
                    print("❌ Konu analizi yapılmadı. Ana menüden seçenek 2 veya 3'ü seçin.")
            elif sub_choice == '8':
                print("\n📁 OLUŞTURULAN DOSYALAR:")
                print("-" * 40)
                print("📊 sentiment_analysis.json - Detaylı sentiment analizi")
                print("🧠 topic_analysis.json - Konu çıkarımı (JSON)")
                print("📄 topic_report.txt - Konu analizi raporu")
                print("🤖 ai_summary.txt - AI genel özeti")
                print("🚚 kargo_sikayetler.txt - Kargo şikayetleri")
                print("⭐ kalite_ovguler.txt - Kalite övgüleri")
            elif sub_choice == '9':
                print("👋 Sistem kapatılıyor...")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 1-9 arası bir sayı girin.")

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

def quick_topic_demo():
    """Hızlı konu analizi demo"""
    print("🎯 HIZLI KONU ANALİZİ DEMO")
    print("="*40)
    
    topic_analyzer = TopicModelingAnalyzer()
    comments = topic_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if len(comments) < 5:
        print("❌ Demo için en az 5 yorum gerekli!")
        return
    
    # Sadece LDA ile hızlı analiz
    texts = [comment.get('comment', '') for comment in comments[:50]]  # İlk 50 yorum
    
    print("🤖 LDA ile hızlı konu çıkarımı...")
    lda_result = topic_analyzer.lda_topic_modeling(texts, n_topics=3, n_words=5)
    
    if 'topics' in lda_result:
        print("\n📋 BULUNAN KONULAR:")
        for topic in lda_result['topics']:
            print(f"   🔹 {topic['topic_name']}: {', '.join(topic['words'][:3])}")
    else:
        print("❌ Konu çıkarımı başarısız")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        quick_topic_demo()
    else:
        main() 