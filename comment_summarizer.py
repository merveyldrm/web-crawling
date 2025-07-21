import csv
import json
from collections import Counter
import re
from datetime import datetime

class CommentSummarizer:
    def __init__(self):
        self.stop_words = {
            've', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'çok', 'güzel', 'iyi', 'kargo',
            'aldım', 'aldık', 'beğendik', 'beğendi', 'teşekkür', 'ediyorum', 'ederiz',
            'oldu', 'geldi', 'paketleme', 'hızlı', 'sağlam', 'orijinal', 'kaliteli',
            'ürün', 'telefon', 'iphone', 'eşime', 'kızıma', 'oğluma', 'kardeşime',
            'hediye', 'olarak', 'tavsiye', 'ediyorum', 'ediyoruz', 'güvenilir',
            'sorunsuz', 'memnun', 'kaldık', 'kaldım', 'çok', 'çok', 'çok'
        }
    
    def load_comments_from_csv(self, filename):
        """CSV dosyasından yorumları yükler"""
        comments = []
        try:
            with open(filename, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    comments.append(row)
            print(f"{len(comments)} yorum yüklendi: {filename}")
            return comments
        except Exception as e:
            print(f"CSV dosyası okuma hatası: {e}")
            return []
    
    def load_comments_from_txt(self, filename):
        """TXT dosyasından yorumları yükler"""
        comments = []
        try:
            with open(filename, 'r', encoding='utf-8') as txtfile:
                content = txtfile.read()
                
            # Yorumları parse et
            comment_blocks = content.split('=== YORUM')
            
            for block in comment_blocks[1:]:  # İlk boş bloğu atla
                comment_data = {}
                
                # Kullanıcı
                user_match = re.search(r'Kullanıcı:\s*(.+)', block)
                if user_match:
                    comment_data['user'] = user_match.group(1).strip()
                
                # Tarih
                date_match = re.search(r'Tarih:\s*(.+)', block)
                if date_match:
                    comment_data['date'] = date_match.group(1).strip()
                
                # Puan
                rating_match = re.search(r'Puan:\s*(.+)', block)
                if rating_match:
                    comment_data['rating'] = rating_match.group(1).strip()
                
                # Satıcı
                seller_match = re.search(r'Satıcı:\s*(.+)', block)
                if seller_match:
                    comment_data['seller'] = seller_match.group(1).strip()
                
                # Yorum
                comment_match = re.search(r'Yorum:\s*(.+)', block, re.DOTALL)
                if comment_match:
                    comment_data['comment'] = comment_match.group(1).strip()
                
                if comment_data.get('comment'):
                    comments.append(comment_data)
            
            print(f"{len(comments)} yorum yüklendi: {filename}")
            return comments
            
        except Exception as e:
            print(f"TXT dosyası okuma hatası: {e}")
            return []
    
    def clean_text(self, text):
        """Metni temizler ve normalize eder"""
        if not text:
            return ""
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Türkçe karakterleri normalize et
        text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        
        # Özel karakterleri kaldır
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, comments, min_frequency=2):
        """Yorumlardan anahtar kelimeleri çıkarır"""
        all_words = []
        
        for comment in comments:
            text = comment.get('comment', '')
            if text:
                # Metni temizle
                clean_text = self.clean_text(text)
                
                # Kelimelere ayır
                words = clean_text.split()
                
                # Stop words'leri filtrele
                filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
                
                all_words.extend(filtered_words)
        
        # Kelime frekanslarını hesapla
        word_freq = Counter(all_words)
        
        # Minimum frekans filtresi uygula
        keywords = {word: freq for word, freq in word_freq.items() if freq >= min_frequency}
        
        return dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_sentiment(self, comments):
        """Basit duygu analizi yapar"""
        positive_words = {
            'güzel', 'iyi', 'mükemmel', 'harika', 'süper', 'kaliteli', 'hızlı', 'sağlam',
            'beğendik', 'beğendi', 'memnun', 'tavsiye', 'teşekkür', 'orijinal', 'sorunsuz'
        }
        
        negative_words = {
            'kötü', 'berbat', 'kırık', 'bozuk', 'yavaş', 'sorun', 'problem', 'memnun değil',
            'beğenmedim', 'tavsiye etmem', 'para israfı', 'kandırıldım'
        }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for comment in comments:
            text = comment.get('comment', '').lower()
            if text:
                pos_score = sum(1 for word in positive_words if word in text)
                neg_score = sum(1 for word in negative_words if word in text)
                
                if pos_score > neg_score:
                    positive_count += 1
                elif neg_score > pos_score:
                    negative_count += 1
                else:
                    neutral_count += 1
        
        total = len(comments)
        if total > 0:
            return {
                'positive_percentage': round((positive_count / total) * 100, 2),
                'negative_percentage': round((negative_count / total) * 100, 2),
                'neutral_percentage': round((neutral_count / total) * 100, 2),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_count': total
            }
        return {}
    
    def analyze_ratings(self, comments):
        """Puan analizi yapar"""
        ratings = []
        for comment in comments:
            rating = comment.get('rating', '')
            if rating and rating.isdigit():
                ratings.append(int(rating))
        
        if ratings:
            return {
                'average_rating': round(sum(ratings) / len(ratings), 2),
                'total_ratings': len(ratings),
                'rating_distribution': dict(Counter(ratings))
            }
        return {}
    
    def analyze_sellers(self, comments):
        """Satıcı analizi yapar"""
        sellers = [comment.get('seller', 'Bilinmiyor') for comment in comments]
        seller_freq = Counter(sellers)
        return dict(seller_freq.most_common())
    
    def generate_summary(self, comments):
        """Kapsamlı özet oluşturur"""
        if not comments:
            return {}
        
        summary = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_comments': len(comments),
            'keywords': self.extract_keywords(comments),
            'sentiment': self.analyze_sentiment(comments),
            'ratings': self.analyze_ratings(comments),
            'sellers': self.analyze_sellers(comments),
            'sample_comments': []
        }
        
        # Add summary paragraph
        summary['summary_paragraph'] = self.generate_summary_paragraph(comments)
        # Örnek yorumlar (ilk 5'i)
        for comment in comments[:5]:
            summary['sample_comments'].append({
                'user': comment.get('user', 'Anonim'),
                'comment': comment.get('comment', '')[:100] + '...' if len(comment.get('comment', '')) > 100 else comment.get('comment', ''),
                'rating': comment.get('rating', 'Bilinmiyor'),
                'seller': comment.get('seller', 'Bilinmiyor')
            })
        
        return summary
    
    def save_summary_to_txt(self, summary, filename='comment_summary.txt'):
        """Özeti TXT dosyasına kaydeder"""
        try:
            with open(filename, 'w', encoding='utf-8') as txtfile:
                txtfile.write("=" * 60 + "\n")
                txtfile.write("YORUM ANALİZ ÖZETİ\n")
                txtfile.write("=" * 60 + "\n\n")
                
                txtfile.write(f"Oluşturulma Tarihi: {summary['generated_at']}\n")
                txtfile.write(f"Toplam Yorum Sayısı: {summary['total_comments']}\n\n")
                
                # Tek paragraf özet
                if 'summary_paragraph' in summary:
                    txtfile.write("ÜRÜN HAKKINDA GENEL ÖZET:\n")
                    txtfile.write("-" * 20 + "\n")
                    txtfile.write(summary['summary_paragraph'] + "\n\n")
                
                # Duygu Analizi
                sentiment = summary['sentiment']
                txtfile.write("DUYGU ANALİZİ:\n")
                txtfile.write("-" * 20 + "\n")
                txtfile.write(f"Pozitif: %{sentiment['positive_percentage']} ({sentiment['positive_count']} yorum)\n")
                txtfile.write(f"Negatif: %{sentiment['negative_percentage']} ({sentiment['negative_count']} yorum)\n")
                txtfile.write(f"Nötr: %{sentiment['neutral_percentage']} ({sentiment['neutral_count']} yorum)\n\n")
                
                # Puan Analizi
                ratings = summary['ratings']
                if ratings:
                    txtfile.write("PUAN ANALİZİ:\n")
                    txtfile.write("-" * 20 + "\n")
                    txtfile.write(f"Ortalama Puan: {ratings['average_rating']}/5\n")
                    txtfile.write(f"Toplam Puanlı Yorum: {ratings['total_ratings']}\n")
                    txtfile.write("Puan Dağılımı:\n")
                    for rating, count in sorted(ratings['rating_distribution'].items()):
                        txtfile.write(f"  {rating} yıldız: {count} yorum\n")
                    txtfile.write("\n")
                
                # Satıcı Analizi
                sellers = summary['sellers']
                txtfile.write("SATICI ANALİZİ:\n")
                txtfile.write("-" * 20 + "\n")
                for seller, count in sellers.items():
                    percentage = round((count / summary['total_comments']) * 100, 1)
                    txtfile.write(f"{seller}: {count} yorum (%{percentage})\n")
                txtfile.write("\n")
                
                # Anahtar Kelimeler
                keywords = summary['keywords']
                txtfile.write("EN SIK KULLANILAN KELİMELER:\n")
                txtfile.write("-" * 30 + "\n")
                for i, (word, freq) in enumerate(list(keywords.items())[:20], 1):
                    txtfile.write(f"{i:2d}. {word}: {freq} kez\n")
                txtfile.write("\n")
                
                txtfile.write("=" * 60 + "\n")
                txtfile.write("ÖZET TAMAMLANDI\n")
                txtfile.write("=" * 60 + "\n")
            
            print(f"Özet başarıyla kaydedildi: {filename}")
            
        except Exception as e:
            print(f"Özet kaydetme hatası: {e}")
    
    def save_summary_to_json(self, summary, filename='comment_summary.json'):
        """Özeti JSON dosyasına kaydeder"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(summary, jsonfile, ensure_ascii=False, indent=2)
            print(f"JSON özeti kaydedildi: {filename}")
        except Exception as e:
            print(f"JSON kaydetme hatası: {e}")

    def generate_summary_paragraph(self, comments):
        """
        Returns a single paragraph summary for the product, highlighting the general sentiment, average rating, and most repeated positive/negative points.
        """
        if not comments:
            return "No comments found."

        positive_phrases = [
            'fiyat performans', 'kalite', 'hızlı kargo', 'mükemmel', 'harika', 'sağlam', 'memnun', 'tavsiye', 'güzel', 'iyi', 'orijinal', 'teşekkür', 'uygun fiyat', 'paketleme güzel', 'beklentiyi karşıladı', 'beğendim', 'beğendik', 'süper', 'kaliteli', 'sorunsuz'
        ]
        negative_phrases = [
            'kargo yavaş', 'kırık', 'bozuk', 'geç geldi', 'sorun', 'problem', 'memnun değilim', 'beğenmedim', 'tavsiye etmem', 'para israfı', 'kandırıldım', 'kalitesiz', 'eksik', 'hasarlı', 'paketleme kötü', 'iade', 'uygun değil', 'berbat', 'kötü', 'yavaş'
        ]

        pos_counter = {}
        neg_counter = {}

        for comment in comments:
            text = self.clean_text(comment.get('comment', ''))
            for phrase in positive_phrases:
                if phrase in text:
                    pos_counter[phrase] = pos_counter.get(phrase, 0) + 1
            for phrase in negative_phrases:
                if phrase in text:
                    neg_counter[phrase] = neg_counter.get(phrase, 0) + 1

        top_pos = sorted(pos_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        top_neg = sorted(neg_counter.items(), key=lambda x: x[1], reverse=True)[:3]

        pos_examples = [f'"{phrase}"' for phrase, count in top_pos if count > 0]
        neg_examples = [f'"{phrase}"' for phrase, count in top_neg if count > 0]

        sentiment = self.analyze_sentiment(comments)
        ratings = self.analyze_ratings(comments)
        pos = sentiment.get('positive_percentage', 0)
        neg = sentiment.get('negative_percentage', 0)
        neu = sentiment.get('neutral_percentage', 0)
        avg_rating = ratings.get('average_rating', None)

        if pos > neg and pos > neu:
            trend = "Most comments are positive"
        elif neg > pos and neg > neu:
            trend = "Most comments are negative"
        else:
            trend = "Most comments are neutral"

        if avg_rating:
            trend += f", average rating: {avg_rating}/5"

        paragraph = f"{trend}. "
        paragraph += "Positive highlights: "
        if pos_examples:
            paragraph += ", ".join(pos_examples)
        else:
            paragraph += "no prominent positive points"
        paragraph += ". "

        paragraph += "Negative highlights: "
        if neg_examples:
            paragraph += ", ".join(neg_examples)
        else:
            paragraph += "no prominent negative points"
        paragraph += "."

        return paragraph

    def extract_pros_cons(self, comments, top_n=5):
        """
        Yorumlardan en sık geçen artı (pros) ve eksi (cons) özellikleri madde madde çıkarır.
        """
        # Pozitif ve negatif anahtar ifadeler
        positive_phrases = [
            'fiyat performans', 'kalite', 'hızlı kargo', 'mükemmel', 'harika', 'sağlam', 'memnun', 'tavsiye',
            'güzel', 'iyi', 'orijinal', 'teşekkür', 'uygun fiyat', 'paketleme güzel', 'beklentiyi karşıladı',
            'beğendim', 'beğendik', 'süper', 'kaliteli', 'sorunsuz', 'kullanışlı', 'bayıldı', 'hemen geldi',
            'indirimli', 'uygun fiyatlı', 'hızlı teslimat', 'hediye', 'beğendi', 'çok güzel', 'çok iyi'
        ]
        negative_phrases = [
            'kargo yavaş', 'kırık', 'bozuk', 'geç geldi', 'sorun', 'problem', 'memnun değilim', 'beğenmedim',
            'tavsiye etmem', 'para israfı', 'kandırıldım', 'kalitesiz', 'eksik', 'hasarlı', 'paketleme kötü',
            'iade', 'uygun değil', 'berbat', 'kötü', 'yavaş', 'küçük geldi', 'büyük geldi', 'renk farklı',
            'model farklı', 'uyumsuz', 'beden olmadı', 'beden küçük', 'beden büyük', 'renk soluk', 'eksik parça'
        ]

        pros_counter = {}
        cons_counter = {}

        for comment in comments:
            text = self.clean_text(comment.get('comment', ''))
            for phrase in positive_phrases:
                if phrase in text:
                    pros_counter[phrase] = pros_counter.get(phrase, 0) + 1
            for phrase in negative_phrases:
                if phrase in text:
                    cons_counter[phrase] = cons_counter.get(phrase, 0) + 1

        top_pros = sorted(pros_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_cons = sorted(cons_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]

        pros_list = [f"{phrase} ({count} yorum)" for phrase, count in top_pros if count > 0]
        cons_list = [f"{phrase} ({count} yorum)" for phrase, count in top_cons if count > 0]

        return {
            'pros': pros_list,
            'cons': cons_list
        }

    def category_analysis(self, comments, include_beden_renk=False, top_n=3):
        """
        Kalite, kargo, fiyat, beden/uyum, renk/model gibi kategoriler için anahtar kelime kümeleriyle analiz yapar.
        Beden/uyum ve renk/model analizleri opsiyoneldir.
        """
        categories = {
            'kalite': ['kalite', 'kaliteli', 'kalitesiz', 'sağlam', 'dayanıklı', 'bozuk', 'kırık', 'hasarlı', 'orijinal'],
            'kargo': ['kargo', 'hızlı kargo', 'geç geldi', 'hızlı teslimat', 'yavaş', 'paketleme', 'paketleme güzel', 'paketleme kötü', 'teslimat'],
            'fiyat': ['fiyat', 'uygun fiyat', 'pahalı', 'indirim', 'fiyat performans', 'indirimli', 'ucuz', 'değer', 'para israfı'],
        }
        if include_beden_renk:
            categories['beden_uyum'] = ['beden', 'uyum', 'uydu', 'olmadı', 'küçük geldi', 'büyük geldi', 'tam oldu', 'uyumsuz', 'beden küçük', 'beden büyük']
            categories['renk_model'] = ['renk', 'model', 'renk farklı', 'model farklı', 'renk soluk', 'renk canlı', 'desen', 'görseldeki gibi', 'görselden farklı']

        results = {}
        for cat, keywords in categories.items():
            count = 0
            example_sentences = []
            for comment in comments:
                text = comment.get('comment', '')
                clean = self.clean_text(text)
                for kw in keywords:
                    if kw in clean:
                        count += 1
                        if len(example_sentences) < top_n:
                            # Orijinal cümleyi ekle
                            example_sentences.append(text.strip()[:120] + ("..." if len(text.strip()) > 120 else ""))
                        break
            results[cat] = {
                'count': count,
                'examples': example_sentences
            }
        return results

    def generate_ai_summary(self, comments, include_beden_renk=False):
        """
        AI Destekli Özet: Genel değerlendirme, artı/eksi özellikler, kategorik analiz, opsiyonel beden/uyum ve renk/model, satıcı değerlendirmesi.
        """
        summary = {}
        # Genel ürün değerlendirmesi (tek paragraf)
        summary['genel_degerlendirme'] = self.generate_summary_paragraph(comments)
        # Artı/Eksi özellikler
        summary['arti_eksi_ozellikler'] = self.extract_pros_cons(comments)
        # Kategorik analiz
        summary['kategorik_analiz'] = self.category_analysis(comments, include_beden_renk=include_beden_renk)
        # Satıcı değerlendirmesi
        summary['satici_degerlendirmesi'] = self.analyze_sellers(comments)
        # Toplam yorum sayısı
        summary['toplam_yorum'] = len(comments)
        return summary

    def save_ai_summary_to_txt(self, summary, filename='comment_summary.txt'):
        """AI özetini TXT dosyasına kaydeder"""
        try:
            with open(filename, 'w', encoding='utf-8') as txtfile:
                txtfile.write("AI Destekli Özet\n")
                txtfile.write("="*20 + "\n\n")

                # Genel ürün değerlendirmesi
                txtfile.write("Genel ürün değerlendirmesi\n")
                txtfile.write("-" * 20 + "\n")
                txtfile.write(summary.get('genel_degerlendirme', 'Değerlendirme bulunamadı.') + "\n\n")

                # Artı/eksi özellikler ayrımı
                pros_cons = summary.get('arti_eksi_ozellikler', {})
                txtfile.write("Artı/eksi özellikler ayrımı\n")
                txtfile.write("-" * 20 + "\n")
                txtfile.write("Artılar:\n")
                if pros_cons.get('pros'):
                    for pro in pros_cons['pros']:
                        txtfile.write(f"- {pro}\n")
                else:
                    txtfile.write("- Belirgin bir artı özellik bulunamadı.\n")
                txtfile.write("\nEksiler:\n")
                if pros_cons.get('cons'):
                    for con in pros_cons['cons']:
                        txtfile.write(f"- {con}\n")
                else:
                    txtfile.write("- Belirgin bir eksi özellik bulunamadı.\n")
                txtfile.write("\n")

                # Kalite, kargo, fiyat gibi kategorik analiz
                kategorik = summary.get('kategorik_analiz', {})
                txtfile.write("Kalite, kargo, fiyat gibi kategorik analiz\n")
                txtfile.write("-" * 20 + "\n")
                for kategori, data in kategorik.items():
                    txtfile.write(f"{kategori.replace('_', ' ').title()}:\n")
                    txtfile.write(f"  - {data.get('count', 0)} yorumda bahsedildi.\n")
                    if data.get('examples'):
                        txtfile.write("  - Örnek yorumlar:\n")
                        for ex in data['examples']:
                            txtfile.write(f'    -"{ex}"\n')
                txtfile.write("\n")
                
                # Beden/uyum bilgileri (tekstil ürünleri için)
                if 'beden_uyum' in kategorik:
                    beden_uyum = kategorik['beden_uyum']
                    txtfile.write("Beden/uyum bilgileri\n")
                    txtfile.write("-" * 20 + "\n")
                    txtfile.write(f"  - {beden_uyum.get('count', 0)} yorumda bahsedildi.\n")
                    if beden_uyum.get('examples'):
                        txtfile.write("  - Örnek yorumlar:\n")
                        for ex in beden_uyum['examples']:
                            txtfile.write(f'    -"{ex}"\n')
                    txtfile.write("\n")

                # Renk/model varyasyonu yorumları
                if 'renk_model' in kategorik:
                    renk_model = kategorik['renk_model']
                    txtfile.write("Renk/model varyasyonu yorumları\n")
                    txtfile.write("-" * 20 + "\n")
                    txtfile.write(f"  - {renk_model.get('count', 0)} yorumda bahsedildi.\n")
                    if renk_model.get('examples'):
                        txtfile.write("  - Örnek yorumlar:\n")
                        for ex in renk_model['examples']:
                            txtfile.write(f'    -"{ex}"\n')
                    txtfile.write("\n")


                # Satıcı değerlendirmesi
                satici = summary.get('satici_degerlendirmesi', {})
                txtfile.write("Satıcı değerlendirmesi\n")
                txtfile.write("-" * 20 + "\n")
                if satici:
                    for seller, count in satici.items():
                        txtfile.write(f"- {seller}: {count} yorum\n")
                else:
                    txtfile.write("- Satıcı bilgisi bulunamadı.\n")
                txtfile.write("\n")


            print(f"AI özeti başarıyla kaydedildi: {filename}")
        except Exception as e:
            print(f"AI özeti kaydetme hatası: {e}")

def main():
    summarizer = CommentSummarizer()
    
    # Yorumları CSV'den yükle
    comments = summarizer.load_comments_from_csv("trendyol_comments.csv")
    
    if not comments:
        print("Yorum yüklenemedi!")
        return
    
    # AI Destekli Özet oluştur
    # Tekstil ürünü olup olmadığını anlamak için anahtar kelimeler
    textile_keywords = ['beden', 'kalıp', 'giyim', 'elbise', 'pantolon', 'gömlek', 'etek', 'ceket', 'küçük geldi', 'büyük geldi']
    
    # Yorum metinlerini birleştir
    all_comment_text = " ".join([comment.get('comment', '').lower() for comment in comments])
    
    # Tekstil anahtar kelimelerinden herhangi biri geçiyor mu?
    include_beden_renk = any(keyword in all_comment_text for keyword in textile_keywords)
    
    print("\nAI Destekli Özet oluşturuluyor...")
    ai_summary = summarizer.generate_ai_summary(comments, include_beden_renk=include_beden_renk)
    
    # Özeti TXT dosyasına kaydet
    summarizer.save_ai_summary_to_txt(ai_summary, 'comment_summary.txt')
    
    print("\nİşlem tamamlandı!")

if __name__ == "__main__":
    main()