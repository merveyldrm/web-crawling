from advanced_comment_analyzer import AdvancedCommentAnalyzer
from comment_summarizer import CommentSummarizer
from topic_modeling_analyzer import TopicModelingAnalyzer
from priority_analyzer import PriorityAnalyzer

def main():
    print("🚀 GELİŞMİŞ YORUM ANALİZ SİSTEMİ v3.0")
    print("📊 Sentiment + Kategori + Konu Çıkarımı + Önceliklendirme")
    print("="*70)
    
    # Analizcileri başlat
    advanced_analyzer = AdvancedCommentAnalyzer()
    basic_summarizer = CommentSummarizer()
    topic_analyzer = TopicModelingAnalyzer()
    priority_analyzer = PriorityAnalyzer()
    
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
    print("3. 🚨 Önceliklendirme + Acil Sorun Tespiti")  # YENİ!
    print("4. 🚀 Tüm Analizler (Kapsamlı)")
    print("5. 📋 Sadece Konu Modelleme")
    
    choice = input("\nSeçiminiz (1-5): ").strip()
    
    if choice in ['1', '4']:
        # 1. SENTIMENT + KATEGORİ ANALİZİ
        print("\n🎭 1. Sentiment + Kategori analizi başlıyor...")
        analysis_results = advanced_analyzer.analyze_all_comments(comments)
        
        category_report = advanced_analyzer.generate_category_report(analysis_results)
        print(category_report)
        
        # Dosyaları kaydet
        advanced_analyzer.save_detailed_analysis(analysis_results, 'sentiment_analysis.json')
    
    if choice in ['2', '4', '5']:
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
    
    if choice in ['3', '4']:
        # 3. ÖNCELİKLENDİRME ANALİZİ - YENİ!
        print("\n🚨 3. Önceliklendirme ve acil sorun tespiti başlıyor...")
        
        # Önce sentiment analizi gerekli
        if 'analysis_results' not in locals():
            print("📊 Sentiment analizi yapılıyor (önceliklendirme için gerekli)...")
            analysis_results = advanced_analyzer.analyze_all_comments(comments)
        
        # Öncelik analizi
        priority_results = priority_analyzer.analyze_critical_issues(comments, analysis_results)
        
        if priority_results:
            priority_report = priority_analyzer.generate_priority_report(priority_results)
            print(priority_report)
            
            # Öncelik analizi dosyalarını kaydet
            priority_analyzer.save_priority_analysis(priority_results, 'priority_analysis.json')
            priority_analyzer.save_priority_report(priority_results, 'priority_report.txt')
        else:
            print("❌ Öncelik analizi başarısız!")
    
    if choice == '4':
        # 4. GELENEKSEl AI ÖZET
        print("\n🤖 4. AI destekli genel özet oluşturuluyor...")
        textile_keywords = ['beden', 'kalıp', 'giyim', 'elbise', 'pantolon']
        all_comment_text = " ".join([comment.get('comment', '').lower() for comment in comments])
        include_beden_renk = any(keyword in all_comment_text for keyword in textile_keywords)
        
        ai_summary = basic_summarizer.generate_ai_summary(comments, include_beden_renk=include_beden_renk)
        basic_summarizer.save_ai_summary_to_txt(ai_summary, 'ai_summary.txt')
    
    # 5. İNTERAKTİF MENÜ
    if choice in ['1', '3', '4']:
        print("\n" + "="*70)
        print("✅ ANALİZ TAMAMLANDI!")
        print("="*70)
        
        while True:
            print("\n🔍 Hangi detayı incelemek istiyorsunuz?")
            print("1. 🚚 Kargo şikayetleri")
            print("2. ⭐ Kalite övgüleri") 
            print("3. 💰 Fiyat yorumları")
            print("4. 🎧 Müşteri hizmeti sorunları")
            print("5. 📊 Ürün özellikleri (pozitif)")
            print("6. 👔 Beden/uyum sorunları")
            print("7. 📄 Konu analizi sonuçları")
            print("8. 🚨 Acil müdahale listesi")  # YENİ!
            print("9. 📊 Öncelik skorları")      # YENİ!
            print("10. 📁 Dosya listesi")
            print("11. 🚪 Çıkış")
            
            sub_choice = input("\nSeçiminiz (1-11): ").strip()
            
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
                    show_topic_summary(topic_results)
                else:
                    print("❌ Konu analizi yapılmadı. Ana menüden seçenek 2, 4 veya 5'i seçin.")
            elif sub_choice == '8':
                if 'priority_results' in locals():
                    show_urgent_issues(priority_results)
                else:
                    print("❌ Öncelik analizi yapılmadı. Ana menüden seçenek 3 veya 4'ü seçin.")
            elif sub_choice == '9':
                if 'priority_results' in locals():
                    show_priority_scores(priority_results)
                else:
                    print("❌ Öncelik analizi yapılmadı. Ana menüden seçenek 3 veya 4'ü seçin.")
            elif sub_choice == '10':
                show_file_list()
            elif sub_choice == '11':
                print("👋 Sistem kapatılıyor...")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 1-11 arası bir sayı girin.")

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

def show_topic_summary(topic_results):
    """Konu analizi özetini göster"""
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
            total_docs = topic_results['clustering_analysis']['model_info']['total_documents']
            percentage = round(cluster['size'] / total_docs * 100, 1)
            print(f"   📊 {cluster['topic_name']}: %{percentage} ({cluster['size']} yorum)")

def show_urgent_issues(priority_results):
    """Acil müdahale gerektiren sorunları göster"""
    print("\n🚨 ACİL MÜDAHALE LİSTESİ:")
    print("="*50)
    
    critical_issues = priority_results.get('critical_issues', {})
    
    if not critical_issues:
        print("✅ Acil müdahale gerektiren sorun bulunamadı!")
        return
    
    # 80+ skor alanları göster
    urgent_found = False
    for category, data in critical_issues.items():
        if data['priority_score'] >= 80:
            urgent_found = True
            print(f"\n🔴 {category.upper()} - ACİL!")
            print(f"   📊 Öncelik Skoru: {data['priority_score']}/100")
            print(f"   🏢 Sorumlu Departman: {data['category_info']['department']}")
            print(f"   💬 Şikayet Sayısı: {data['total_negative_comments']}")
            print(f"   📅 Son 7 Günde: {data['recent_complaints']} şikayet")
            
            # En kritik yorumu göster
            if data['issue_details']:
                critical_comment = data['issue_details'][0]
                print(f"   💭 Örnek: \"{critical_comment['comment'][:100]}...\"")
    
    if not urgent_found:
        print("🟡 80+ skor alan acil sorun yok, fakat yüksek öncelik kategoriler mevcut:")
        for category, data in list(critical_issues.items())[:3]:
            if data['priority_score'] >= 60:
                print(f"   🟡 {category.upper()}: {data['priority_score']}/100")

def show_priority_scores(priority_results):
    """Tüm öncelik skorlarını göster"""
    print("\n📊 ÖNCELİK SKOR TABLOSU:")
    print("="*60)
    
    critical_issues = priority_results.get('critical_issues', {})
    
    if not critical_issues:
        print("❌ Öncelik skoru bulunamadı!")
        return
    
    print(f"{'Kategori':<20} {'Skor':<8} {'Şikayet':<10} {'Departman'}")
    print("-" * 60)
    
    for category, data in critical_issues.items():
        score = data['priority_score']
        count = data['total_negative_comments']
        dept = data['category_info']['department'][:15]
        
        # Renk kodlaması
        if score >= 80:
            emoji = "🔴"
        elif score >= 60:
            emoji = "🟡"
        else:
            emoji = "🔵"
        
        print(f"{emoji} {category:<17} {score:<8.1f} {count:<10} {dept}")

def show_file_list():
    """Oluşturulan dosyaları listele"""
    print("\n📁 OLUŞTURULAN DOSYALAR:")
    print("-" * 50)
    print("📊 sentiment_analysis.json - Detaylı sentiment analizi")
    print("🧠 topic_analysis.json - Konu çıkarımı (JSON)")
    print("📄 topic_report.txt - Konu analizi raporu")
    print("🚨 priority_analysis.json - Öncelik analizi (JSON)")
    print("📋 priority_report.txt - Önceliklendirme raporu")
    print("🤖 ai_summary.txt - AI genel özeti")
    print("🚚 kargo_sikayetler.txt - Kargo şikayetleri")
    print("⭐ kalite_ovguler.txt - Kalite övgüleri")

def quick_priority_demo():
    """Hızlı öncelik analizi demo"""
    print("🚨 HIZLI ÖNCELİKLENDİRME DEMO")
    print("="*50)
    
    # Analizcileri başlat
    comment_analyzer = AdvancedCommentAnalyzer()
    priority_analyzer = PriorityAnalyzer()
    
    comments = comment_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if len(comments) < 5:
        print("❌ Demo için en az 5 yorum gerekli!")
        return
    
    # Hızlı sentiment analizi
    print("🎭 Sentiment analizi...")
    sentiment_results = comment_analyzer.analyze_all_comments(comments)
    
    # Öncelik analizi
    print("🚨 Öncelik analizi...")
    priority_results = priority_analyzer.analyze_critical_issues(comments, sentiment_results)
    
    # Sadece en yüksek 3 önceliği göster
    critical_issues = priority_results.get('critical_issues', {})
    
    if critical_issues:
        print(f"\n📊 EN YÜKSEK 3 ÖNCELİK:")
        for i, (category, data) in enumerate(list(critical_issues.items())[:3], 1):
            score = data['priority_score']
            
            if score >= 80:
                emoji = "🔴"
                urgency = "ACİL"
            elif score >= 60:
                emoji = "🟡"
                urgency = "YÜKSEK"
            else:
                emoji = "🔵"
                urgency = "ORTA"
            
            print(f"   {i}. {emoji} {category.upper()}: {score}/100 - {urgency}")
    else:
        print("✅ Kritik seviyede sorun tespit edilmedi!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        quick_priority_demo()
    else:
        main() 