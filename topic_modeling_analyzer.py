import csv
import json
import re
from collections import Counter
from typing import List, Dict, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

# NLTK verilerini indir (ilk çalıştırmada)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TopicModelingAnalyzer:
    def __init__(self):
        # Türkçe stop words genişletilmiş liste
        self.turkish_stop_words = {
            've', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'çok', 'var', 'yok', 'olan',
            'aldım', 'aldık', 'beğendik', 'beğendi', 'teşekkür', 'ediyorum', 'ederiz',
            'oldu', 'geldi', 'hediye', 'olarak', 'ediyorum', 'ediyoruz', 'kaldık', 'kaldım',
            'olan', 'olarak', 'ama', 'fakat', 'ancak', 'şey', 'şu', 'o', 'bana', 'benim',
            'sen', 'sana', 'onun', 'onlar', 'bizim', 'size', 'sizin', 'hiç', 'her',
            'ne', 'nasıl', 'neden', 'nerede', 'kim', 'hangi', 'kadar', 'daha', 'en',
            'çünkü', 'eğer', 'ki', 'ya', 'veya', 'hem', 'gibi', 'kadar', 'sonra',
            'önce', 'şimdi', 'burada', 'orada', 'böyle', 'şöyle', 'artık', 'hala',
            'daha', 'bile', 'sadece', 'yalnız', 'gerçekten', 'çok', 'çok', 'çok'
        }
        
        # SentenceTransformer model (Türkçe destekli)
        self.sentence_model = None
        
    def load_sentence_transformer(self):
        """Sentence transformer modelini yükle"""
        try:
            print("🤖 Embedding modeli yükleniyor...")
            # Türkçe destekli çok dilli model
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Embedding modeli yüklendi")
        except Exception as e:
            print(f"⚠️ Embedding modeli yüklenemedi: {e}")
            print("Pip install sentence-transformers komutu ile yükleyebilirsiniz.")
            self.sentence_model = None
    
    def preprocess_text(self, text: str) -> str:
        """Metin ön işleme"""
        if not text:
            return ""
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Özel karakterleri temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)  # Sayıları kaldır
        text = re.sub(r'\s+', ' ', text)  # Çoklu boşlukları tek boşluğa çevir
        
        # Tokenize et
        try:
            words = word_tokenize(text, language='turkish')
        except:
            words = text.split()
        
        # Stop words'leri filtrele ve kısa kelimeleri kaldır
        filtered_words = [
            word for word in words 
            if word not in self.turkish_stop_words 
            and len(word) > 2 
            and word.isalpha()
        ]
        
        return ' '.join(filtered_words)
    
    def load_comments_from_csv(self, filename: str) -> List[Dict]:
        """CSV'den yorumları yükle"""
        comments = []
        try:
            with open(filename, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('comment', '').strip():
                        comments.append(row)
            print(f"📊 {len(comments)} yorum yüklendi")
            return comments
        except Exception as e:
            print(f"❌ CSV okuma hatası: {e}")
            return []
    
    def lda_topic_modeling(self, texts: List[str], n_topics: int = 5, n_words: int = 10) -> Dict:
        """LDA ile konu modelleme"""
        print(f"🔍 LDA analizi başlıyor ({n_topics} konu)...")
        
        # Ön işleme
        processed_texts = [self.preprocess_text(text) for text in texts]
        processed_texts = [text for text in processed_texts if len(text.split()) >= 3]
        
        if len(processed_texts) < 5:
            return {'error': 'Yeterli metin bulunamadı'}
        
        # TF-IDF vektörizasyon
        vectorizer = TfidfVectorizer(
            max_features=200,
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2),
            stop_words=list(self.turkish_stop_words)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # LDA modeli
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=50,
                learning_method='online'
            )
            
            lda.fit(tfidf_matrix)
            
            # Konuları çıkar
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-n_words:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                top_weights = [topic[i] for i in top_words_idx]
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': top_weights,
                    'topic_name': self._generate_topic_name(top_words)
                })
            
            # Her dokümanın hangi konuya ait olduğunu bul
            doc_topic_probs = lda.transform(tfidf_matrix)
            document_topics = []
            
            for doc_idx, probs in enumerate(doc_topic_probs):
                main_topic = np.argmax(probs)
                confidence = probs[main_topic]
                
                document_topics.append({
                    'document_index': doc_idx,
                    'original_text': texts[doc_idx][:100] + '...',
                    'main_topic': main_topic,
                    'confidence': confidence,
                    'all_probabilities': probs.tolist()
                })
            
            return {
                'method': 'LDA',
                'n_topics': n_topics,
                'topics': topics,
                'document_topics': document_topics,
                'model_info': {
                    'total_documents': len(processed_texts),
                    'vocabulary_size': len(feature_names),
                    'perplexity': lda.perplexity(tfidf_matrix)
                }
            }
            
        except Exception as e:
            return {'error': f'LDA analizi hatası: {e}'}
    
    def embedding_clustering(self, texts: List[str], n_clusters: int = 5) -> Dict:
        """Embedding tabanlı clustering"""
        print(f"🧠 Embedding clustering başlıyor ({n_clusters} küme)...")
        
        if self.sentence_model is None:
            self.load_sentence_transformer()
            if self.sentence_model is None:
                return {'error': 'Embedding modeli yüklenemedi'}
        
        # Metinleri temizle
        clean_texts = []
        original_indices = []
        
        for i, text in enumerate(texts):
            clean_text = self.preprocess_text(text)
            if len(clean_text.split()) >= 3:
                clean_texts.append(text)  # Orijinal metni kullan
                original_indices.append(i)
        
        if len(clean_texts) < n_clusters:
            return {'error': f'Yeterli metin yok (minimum {n_clusters} gerekli)'}
        
        try:
            # Embeddings oluştur
            print("📊 Embeddings oluşturuluyor...")
            embeddings = self.sentence_model.encode(clean_texts, show_progress_bar=True)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Kümeleri analiz et
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append({
                    'text': clean_texts[i],
                    'original_index': original_indices[i],
                    'distance_to_center': np.linalg.norm(embeddings[i] - kmeans.cluster_centers_[label])
                })
            
            # Her küme için temsili kelimeler çıkar
            cluster_topics = []
            for cluster_id, docs in clusters.items():
                # Kümedeki tüm metinleri birleştir
                cluster_text = ' '.join([doc['text'] for doc in docs])
                processed_cluster_text = self.preprocess_text(cluster_text)
                
                # En sık geçen kelimeleri bul
                words = processed_cluster_text.split()
                word_freq = Counter(words)
                top_words = [word for word, count in word_freq.most_common(10)]
                
                # Kümenin merkezine en yakın dokümanı bul
                closest_doc = min(docs, key=lambda x: x['distance_to_center'])
                
                cluster_topics.append({
                    'cluster_id': cluster_id,
                    'size': len(docs),
                    'top_words': top_words,
                    'representative_text': closest_doc['text'][:200] + '...',
                    'topic_name': self._generate_topic_name(top_words),
                    'documents': docs[:5]  # İlk 5 dokümanı sakla
                })
            
            return {
                'method': 'Embedding Clustering',
                'n_clusters': n_clusters,
                'clusters': cluster_topics,
                'model_info': {
                    'total_documents': len(clean_texts),
                    'embedding_dimension': embeddings.shape[1],
                    'inertia': kmeans.inertia_
                }
            }
            
        except Exception as e:
            return {'error': f'Embedding clustering hatası: {e}'}
    
    def _generate_topic_name(self, top_words: List[str]) -> str:
        """Konu için otomatik isim oluştur"""
        if not top_words:
            return "Belirsiz Konu"
        
        # Türkçe konu isimleri için özel kural seti
        topic_patterns = {
            ('kargo', 'teslimat', 'paket', 'gönderi'): 'Kargo & Teslimat',
            ('kalite', 'sağlam', 'dayanıklı', 'bozuk'): 'Ürün Kalitesi',
            ('fiyat', 'ucuz', 'pahalı', 'uygun'): 'Fiyat & Değer',
            ('beden', 'büyük', 'küçük', 'uyum'): 'Beden & Uyum',
            ('renk', 'görsel', 'resim', 'fotoğraf'): 'Görsel & Renk',
            ('hizmet', 'müşteri', 'destek', 'yardım'): 'Müşteri Hizmeti',
            ('hızlı', 'yavaş', 'zaman', 'geç'): 'Hız & Zaman',
            ('güzel', 'beğen', 'memnun', 'tavsiye'): 'Genel Memnuniyet',
            ('problem', 'sorun', 'şikayet', 'kötü'): 'Sorunlar & Şikayetler'
        }
        
        # Pattern matching
        top_words_set = set(top_words[:5])
        for pattern, name in topic_patterns.items():
            if any(word in top_words_set for word in pattern):
                return name
        
        # Pattern bulunamazsa ilk 3 kelimeyi kullan
        return ' & '.join(top_words[:3]).title()
    
    def analyze_topics(self, comments: List[Dict], lda_topics: int = 6, cluster_topics: int = 6) -> Dict:
        """Kapsamlı konu analizi"""
        texts = [comment.get('comment', '') for comment in comments if comment.get('comment', '').strip()]
        
        if len(texts) < 10:
            return {'error': 'En az 10 yorum gerekli'}
        
        print(f"🔍 {len(texts)} yorum üzerinde konu analizi başlıyor...")
        
        results = {
            'total_comments': len(texts),
            'lda_analysis': {},
            'clustering_analysis': {},
            'comparison': {},
            'recommendations': []
        }
        
        # LDA analizi
        lda_result = self.lda_topic_modeling(texts, n_topics=lda_topics)
        results['lda_analysis'] = lda_result
        
        # Embedding clustering
        clustering_result = self.embedding_clustering(texts, n_clusters=cluster_topics)
        results['clustering_analysis'] = clustering_result
        
        # Karşılaştırma ve öneriler
        results['comparison'] = self._compare_methods(lda_result, clustering_result)
        results['recommendations'] = self._generate_recommendations(lda_result, clustering_result)
        
        return results
    
    def _compare_methods(self, lda_result: Dict, clustering_result: Dict) -> Dict:
        """İki metodu karşılaştır"""
        comparison = {
            'method_comparison': {
                'LDA': {
                    'strength': 'İstatistiksel konu çıkarımı, kelime ağırlıkları',
                    'weakness': 'Kısa metinlerde daha az etkili'
                },
                'Clustering': {
                    'strength': 'Semantik benzerlik, kısa metinlerde etkili',
                    'weakness': 'Daha fazla hesaplama gücü gerektirir'
                }
            }
        }
        
        # Her iki metodda da ortak konuları bul
        if 'topics' in lda_result and 'clusters' in clustering_result:
            lda_topics = [topic['topic_name'] for topic in lda_result['topics']]
            cluster_topics = [cluster['topic_name'] for cluster in clustering_result['clusters']]
            
            comparison['common_themes'] = list(set(lda_topics) & set(cluster_topics))
            comparison['lda_unique'] = list(set(lda_topics) - set(cluster_topics))
            comparison['clustering_unique'] = list(set(cluster_topics) - set(lda_topics))
        
        return comparison
    
    def _generate_recommendations(self, lda_result: Dict, clustering_result: Dict) -> List[str]:
        """Analiz sonuçlarına göre öneriler oluştur"""
        recommendations = []
        
        # LDA sonuçlarına göre öneriler
        if 'topics' in lda_result:
            for topic in lda_result['topics']:
                top_word = topic['words'][0] if topic['words'] else ''
                if 'kargo' in top_word or 'teslimat' in top_word:
                    recommendations.append("🚚 Kargo/teslimat konusu önemli - lojistik süreçleri gözden geçirin")
                elif 'kalite' in top_word or 'bozuk' in top_word:
                    recommendations.append("🔧 Ürün kalitesi konusu önemli - QC süreçlerini güçlendirin")
                elif 'fiyat' in top_word or 'pahalı' in top_word:
                    recommendations.append("💰 Fiyat konusu önemli - fiyatlandırma stratejinizi gözden geçirin")
        
        # Clustering sonuçlarına göre öneriler
        if 'clusters' in clustering_result:
            large_clusters = [c for c in clustering_result['clusters'] if c['size'] > len(clustering_result['clusters']) * 0.2]
            for cluster in large_clusters:
                recommendations.append(f"📊 '{cluster['topic_name']}' konusu yorumların %{round(cluster['size']/clustering_result['model_info']['total_documents']*100)}ini oluşturuyor")
        
        if not recommendations:
            recommendations.append("📈 Yorum sayısı az, daha fazla veri toplandıktan sonra detaylı analiz yapılabilir")
        
        return recommendations
    
    def generate_topic_report(self, analysis_results: Dict) -> str:
        """Detaylı konu analizi raporu oluştur"""
        report = []
        report.append("🔍 OTOMATIK KONU ÇIKARIMI RAPORU")
        report.append("=" * 60)
        
        total_comments = analysis_results.get('total_comments', 0)
        report.append(f"\n📊 Analiz Edilen Yorum Sayısı: {total_comments}")
        
        # LDA Sonuçları
        lda_result = analysis_results.get('lda_analysis', {})
        if 'topics' in lda_result:
            report.append(f"\n🤖 LDA KONU ANALİZİ")
            report.append("-" * 40)
            
            for topic in lda_result['topics']:
                report.append(f"\n📋 Konu {topic['topic_id'] + 1}: {topic['topic_name']}")
                report.append(f"   🔑 Anahtar Kelimeler: {', '.join(topic['words'][:5])}")
        
        # Clustering Sonuçları
        clustering_result = analysis_results.get('clustering_analysis', {})
        if 'clusters' in clustering_result:
            report.append(f"\n🧠 EMBEDDING CLUSTERING ANALİZİ")
            report.append("-" * 40)
            
            for cluster in clustering_result['clusters']:
                percentage = round(cluster['size'] / clustering_result['model_info']['total_documents'] * 100, 1)
                report.append(f"\n📊 Küme {cluster['cluster_id'] + 1}: {cluster['topic_name']}")
                report.append(f"   📈 Yorum Sayısı: {cluster['size']} (%{percentage})")
                report.append(f"   🔑 Anahtar Kelimeler: {', '.join(cluster['top_words'][:5])}")
                report.append(f"   💬 Örnek: {cluster['representative_text']}")
        
        # Karşılaştırma
        comparison = analysis_results.get('comparison', {})
        if 'common_themes' in comparison and comparison['common_themes']:
            report.append(f"\n🔄 ORTAK KONULAR")
            report.append("-" * 40)
            for theme in comparison['common_themes']:
                report.append(f"   ✅ {theme}")
        
        # Öneriler
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            report.append(f"\n💡 ÖNERİLER")
            report.append("-" * 40)
            for rec in recommendations:
                report.append(f"   {rec}")
        
        return '\n'.join(report)
    
    def save_topic_analysis(self, analysis_results: Dict, filename: str = 'topic_analysis.json'):
        """Konu analizi sonuçlarını kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
            print(f"📁 Konu analizi {filename} dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
    
    def save_topic_report(self, analysis_results: Dict, filename: str = 'topic_report.txt'):
        """Konu analizi raporunu metin olarak kaydet"""
        try:
            report = self.generate_topic_report(analysis_results)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Konu raporu {filename} dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Rapor kaydetme hatası: {e}")


def main():
    """Topic modeling örnek kullanım"""
    analyzer = TopicModelingAnalyzer()
    
    # Yorumları yükle
    comments = analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if not comments:
        print("❌ Yorum yüklenemedi!")
        return
    
    if len(comments) < 10:
        print("⚠️ En az 10 yorum gerekli!")
        return
    
    print("\n🚀 OTOMATIK KONU ÇIKARIMİ SİSTEMİ")
    print("=" * 50)
    
    # Konu analizini yap
    analysis_results = analyzer.analyze_topics(comments, lda_topics=6, cluster_topics=6)
    
    if 'error' in analysis_results:
        print(f"❌ Analiz hatası: {analysis_results['error']}")
        return
    
    # Raporu göster
    report = analyzer.generate_topic_report(analysis_results)
    print("\n" + report)
    
    # Sonuçları kaydet
    analyzer.save_topic_analysis(analysis_results, 'topic_analysis.json')
    analyzer.save_topic_report(analysis_results, 'topic_report.txt')
    
    print(f"\n✅ Analiz tamamlandı!")
    print(f"📁 Detaylı sonuçlar: topic_analysis.json")
    print(f"📄 Rapor: topic_report.txt")


if __name__ == "__main__":
    main() 