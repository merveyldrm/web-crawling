import csv
import json
from collections import Counter, defaultdict
from typing import Dict, List
from contextual_keyword_analyzer import ContextualKeywordAnalyzer

class AdvancedCommentAnalyzer:
    def __init__(self):
        # Bağlamsal analizcıyı ekle
        self.contextual_analyzer = ContextualKeywordAnalyzer()
        
        self.categories = {
            'kargo': {
                'keywords': ['kargo', 'gönderi', 'teslimat', 'paket', 'hızlı', 'yavaş', 'geç'],
                'positive': ['hızlı', 'zamanında', 'sağlam'],
                'negative': ['yavaş', 'geç', 'hasarlı', 'problem', 'çok yavaş', 'çok geç', 'kırık','bozuk']
            },
            'kalite': {
                'keywords': ['kalite', 'sağlam', 'dayanıklı', 'bozuk'],
                'positive': ['kaliteli', 'sağlam', 'dayanıklı'],
                'negative': ['kalitesiz', 'zayıf', 'bozuk']
            },
            'fiyat': {
                'keywords': ['fiyat', 'ucuz', 'pahalı', 'uygun'],
                'positive': ['ucuz', 'uygun', 'değer'],
                'negative': ['pahalı', 'değmez']
            },
            'musteri_hizmeti': {
                'keywords': ['müşteri', 'hizmet', 'destek'],
                'positive': ['memnun', 'yardımcı'],
                'negative': ['memnuniyetsiz', 'kaba']
            },
            'urun_ozellikleri': {
                'keywords': ['özellik', 'çalışıyor', 'performans'],
                'positive': ['mükemmel', 'çalışıyor'],
                'negative': ['çalışmıyor', 'bozuk']
            },
            'beden_uyum': {
                'keywords': ['beden', 'uyum', 'büyük', 'küçük'],
                'positive': ['uydu', 'tam oldu'],
                'negative': ['uymadı', 'büyük geldi', 'küçük geldi']
            }
        }

    def load_comments_from_csv(self, filename: str) -> List[Dict]:
        comments = []
        try:
            with open(filename, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    comments.append(row)
            return comments
        except Exception as e:
            print(f"CSV okuma hatası: {e}")
            return []

    def analyze_comment_categories(self, comment_text: str) -> Dict:
        text_lower = comment_text.lower()
        results = {}
        
        # 1. BAĞLAMSAL ANALİZ İLE BAŞLA
        contextual_result = self.contextual_analyzer.analyze_all_categories(comment_text)
        
        # Hariç tutulan kategorileri işaretle
        excluded_categories = contextual_result.get('summary', {}).get('excluded_categories', [])
        
        for category, data in self.categories.items():
            # Eğer bu kategori bağlamsal analiz tarafından hariç tutulmuşsa
            if category in excluded_categories:
                results[category] = {
                    'relevant': False, 
                    'sentiment': 'neutral', 
                    'keywords_found': [], 
                    'confidence': 0.0,
                    'excluded_by_context': True,
                    'exclusion_reason': 'False positive kelime tespit edildi'
                }
                continue
            
            # Normal kelime analizi
            keywords_found = [kw for kw in data['keywords'] if kw in text_lower]
            
            # Bağlamsal analiz sonucunu kontrol et
            if category in contextual_result.get('all_results', {}):
                ctx_result = contextual_result['all_results'][category]
                
                # Bağlamsal analiz bu kategoriyi onayladıysa güçlendir
                if ctx_result['is_valid_category'] and ctx_result['context_score'] > 0:
                    keywords_found.extend(ctx_result['found_keywords'])
                    keywords_found = list(set(keywords_found))  # Duplicates'ları kaldır
            
            if keywords_found:
                positive = [kw for kw in data['positive'] if kw in text_lower]
                negative = [kw for kw in data['negative'] if kw in text_lower]
                sentiment = 'positive' if len(positive) > len(negative) else 'negative' if negative else 'neutral'
                
                # Bağlamsal güven skorunu da ekle
                base_confidence = min(len(keywords_found) / 2, 1.0)
                contextual_boost = 0
                
                if category in contextual_result.get('all_results', {}):
                    ctx_data = contextual_result['all_results'][category]
                    if ctx_data['is_valid_category']:
                        contextual_boost = ctx_data['analysis_details']['confidence'] / 100
                
                final_confidence = min(base_confidence + contextual_boost, 1.0)
                
                results[category] = {
                    'relevant': True,
                    'sentiment': sentiment,
                    'keywords_found': keywords_found,
                    'confidence': final_confidence,
                    'excluded_by_context': False,
                    'contextual_boost': contextual_boost
                }
            else:
                results[category] = {
                    'relevant': False, 
                    'sentiment': 'neutral', 
                    'keywords_found': [], 
                    'confidence': 0.0,
                    'excluded_by_context': False
                }
        
        return results

    def analyze_all_comments(self, comments: List[Dict]) -> Dict:
        results = {'total_comments': len(comments), 'category_analysis': {}, 'filtered_comments': {}}
        
        for category in self.categories.keys():
            results['category_analysis'][category] = {'total_mentions': 0, 'positive': [], 'negative': [], 'neutral': []}
            results['filtered_comments'][category] = {'positive': [], 'negative': [], 'neutral': []}
        
        for i, comment in enumerate(comments):
            comment_text = comment.get('comment', '')
            if not comment_text:
                continue
            
            category_results = self.analyze_comment_categories(comment_text)
            
            for category, analysis in category_results.items():
                if analysis['relevant']:
                    results['category_analysis'][category]['total_mentions'] += 1
                    comment_data = {
                        'comment': comment_text,
                        'user': comment.get('user', ''),
                        'date': comment.get('date', ''),
                        'analysis': analysis
                    }
                    results['category_analysis'][category][analysis['sentiment']].append(comment_data)
                    results['filtered_comments'][category][analysis['sentiment']].append(comment_data)
        
        return results

    def generate_category_report(self, analysis_results: Dict) -> str:
        report = ["🔍 KONU BAZLI SENTIMENT ANALİZİ", "="*50]
        
        for category, data in analysis_results['category_analysis'].items():
            if data['total_mentions'] > 0:
                report.append(f"\n📋 {category.upper()}: {data['total_mentions']} bahsetme")
                report.append(f"   ✅ Pozitif: {len(data['positive'])}")
                report.append(f"   ❌ Negatif: {len(data['negative'])}")
                report.append(f"   ⚪ Nötr: {len(data['neutral'])}")
        
        return "\n".join(report)

    def filter_comments_by_category_sentiment(self, analysis_results: Dict, category: str, sentiment: str = None) -> List[Dict]:
        if category not in analysis_results['filtered_comments']:
            return []
        
        if sentiment:
            return analysis_results['filtered_comments'][category].get(sentiment, [])
        else:
            all_comments = []
            for sent in ['positive', 'negative', 'neutral']:
                all_comments.extend(analysis_results['filtered_comments'][category][sent])
            return all_comments

    def save_detailed_analysis(self, analysis_results: Dict, filename: str):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            print(f"Analiz {filename} dosyasına kaydedildi.")
        except Exception as e:
            print(f"Kaydetme hatası: {e}")

    def save_filtered_report(self, analysis_results: Dict, category: str, sentiment: str, filename: str):
        comments = self.filter_comments_by_category_sentiment(analysis_results, category, sentiment)
        if not comments:
            return
        
        report = [f"{category.upper()} - {sentiment.upper()}", "="*40]
        for i, comment in enumerate(comments, 1):
            report.append(f"\n{i}. {comment['user']}: {comment['comment'][:100]}...")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            print(f"Rapor {filename} dosyasına kaydedildi.")
        except Exception as e:
            print(f"Rapor kaydetme hatası: {e}") 