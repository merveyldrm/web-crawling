import re
import json
from typing import Dict, List, Tuple, Any

class ContextualKeywordAnalyzer:
    def __init__(self):
        # Bağlamsal kargo kelimeleri - sadece gerçek kargo sorunları
        self.contextual_keywords = {
            'kargo': {
                'primary_keywords': {
                    # Doğrudan kargo sorunları
                    'kargo_direct': ['kargo', 'kargoya', 'kargoda', 'kargoyla', 'kargom', 'kargonuz'],
                    'teslimat_direct': ['teslimat', 'teslim', 'gönderi', 'gönderim', 'sevkiyat'],
                    'paket_direct': ['paket', 'pakette', 'paketi', 'paketim', 'paketiniz'],
                },
                'negative_contexts': {
                    # Kargo gecikmesi - bağlamsal kontrol
                    'gecikme_patterns': [
                        r'\b(kargo|teslimat|gönderi|paket)\s*\w*\s*(geç|gecik|ertelenm|bekl)',
                        r'\b(geç|gecik)\w*\s*\w*\s*(gel\w+|ulaş\w+|teslim)',
                        r'\bgelmedi\b',
                        r'\bulaşmadı\b', 
                        r'\bteslim\s*\w*\s*olmadı\b'
                    ],
                    'hasar_patterns': [
                        r'\b(kargo|paket)\s*\w*\s*(hasar|kır|boz|ezil)',
                        r'\b(kırık|hasarlı|bozuk|ezik)\s*\w*\s*(gel|ulaş|teslim)',
                        r'\bpaket\s*\w*\s*içi\s*\w*\s*(dağın|karış)'
                    ],
                    'kayip_patterns': [
                        r'\b(kargo|paket|gönderi)\s*\w*\s*(kay|bulunamad|yok olmuş)',
                        r'\bulaşmadı\b.*\b(hiç|hala|henüz)\b'
                    ]
                },
                'excluded_contexts': {
                    # Bu bağlamlarda "geç" kelimesi kargo problemi DEĞİL
                    'false_positive_patterns': [
                        r'\bvazgeç\w*',  # vazgeçilmez, vazgeçmem
                        r'\bgeç\w*ğ\w*\s*(beri|den|da)',  # geçtiğimden beri
                        r'\bgeç\w*ş\w*',  # geçmiş, geçiş
                        r'\bek\s+gıda\w*\s+geç',  # ek gıdaya geçtik
                        r'\bbesin\w*\s+geç',  # besine geçtik
                        r'\bmama\w*\s+geç',  # mamaya geçtik
                        r'\büründen\s+geç',  # üründen geçtik
                        r'\bmarka\w*\s+geç',  # markaya geçtik
                        r'\bkullanmaya\s+geç',  # kullanmaya geçtik
                        r'\bsevmeye\s+geç',  # sevmeye geçtik
                        r'\btercih\s+geç',  # tercih etmeye geçtik
                    ]
                }
            },
            'kalite': {
                'primary_keywords': ['kalite', 'bozuk', 'defolu', 'kırık', 'çalışmıyor'],
                'negative_contexts': {
                    'malzeme_patterns': [
                        r'\b(malzeme|yapım|üretim)\s*\w*\s*(kötü|berbat|kalitesiz)',
                        r'\bkırık\s*(gel|çık|ulaş)',
                        r'\bdefolu\s*(ürün|mal|paket)'
                    ]
                },
                'excluded_contexts': {
                    'false_positive_patterns': [
                        r'\bkırınt\w*',  # kırıntı, kırıntısı
                        r'\bkırım\w*',   # kırım, kırımlı
                    ]
                }
            },
            'beden_uyum': {
                'primary_keywords': ['beden', 'kalıp', 'uyum', 'büyük', 'küçük'],
                'negative_contexts': {
                    'uyumsuzluk_patterns': [
                        r'\bbeden\s*\w*\s*(uyma|büyük|küçük|dar|bol)',
                        r'\b(çok|hiç)\s*\w*\s*(büyük|küçük)\s*(gel|çık)',
                        r'\bkalıp\s*\w*\s*(kötü|yanlış|hatalı)'
                    ]
                },
                'excluded_contexts': {
                    'false_positive_patterns': [
                        r'\bbüyük\s*(memnun|beğen|sev)',  # büyük memnuniyet
                        r'\bküçük\s*(beğen|sev|güzel)',   # küçük ama güzel
                        r'\bbeden\s*tablosu\s*(doğru|uygun)'  # beden tablosu doğru
                    ]
                }
            }
        }
        
        # Pozitif bağlam kontrolleri
        self.positive_indicators = [
            r'\bmemnun\w*',
            r'\bbeğen\w*', 
            r'\bsev\w*',
            r'\biyi\b',
            r'\bgüzel\b',
            r'\btavsiye\s*(eder|ediyorum)',
            r'\böneririm\b',
            r'\bkaliteli\b',
            r'\bmükemmel\b'
        ]

    def analyze_contextual_keywords(self, text: str, category: str) -> Dict:
        """Bağlamsal kelime analizi"""
        
        result = {
            'category': category,
            'found_keywords': [],
            'context_score': 0,
            'is_valid_category': False,
            'analysis_details': {
                'positive_context': False,
                'negative_context': False,
                'excluded_by_context': False,
                'pattern_matches': [],
                'excluded_patterns': [],
                'confidence': 0
            }
        }
        
        if category not in self.contextual_keywords:
            return result
        
        text_lower = text.lower()
        category_config = self.contextual_keywords[category]
        
        # 1. EXCLUDED CONTEXT CHECK (False Positive kontrolü)
        excluded_patterns = category_config.get('excluded_contexts', {}).get('false_positive_patterns', [])
        for pattern in excluded_patterns:
            if re.search(pattern, text_lower):
                result['analysis_details']['excluded_by_context'] = True
                result['analysis_details']['excluded_patterns'].append(pattern)
                result['analysis_details']['confidence'] = 0
                return result  # Hemen çık, bu kategori değil
        
        # 2. PRIMARY KEYWORD CHECK
        primary_found = []
        if isinstance(category_config['primary_keywords'], dict):
            # Alt kategoriler varsa
            for sub_cat, keywords in category_config['primary_keywords'].items():
                for keyword in keywords:
                    if keyword in text_lower:
                        primary_found.append(keyword)
        else:
            # Basit liste
            for keyword in category_config['primary_keywords']:
                if keyword in text_lower:
                    primary_found.append(keyword)
        
        result['found_keywords'] = primary_found
        
        # 3. NEGATIVE CONTEXT PATTERNS (Gerçek problemler)
        negative_patterns = category_config.get('negative_contexts', {})
        negative_score = 0
        
        for pattern_type, patterns in negative_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    negative_score += len(matches) * 2  # Negatif pattern daha ağırlıklı
                    result['analysis_details']['pattern_matches'].append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'matches': matches
                    })
        
        if negative_score > 0:
            result['analysis_details']['negative_context'] = True
        
        # 4. POSITIVE CONTEXT CHECK
        positive_score = 0
        for pos_pattern in self.positive_indicators:
            if re.search(pos_pattern, text_lower):
                positive_score += 1
                result['analysis_details']['positive_context'] = True
        
        # 5. FINAL SCORING AND VALIDATION
        if result['analysis_details']['excluded_by_context']:
            # Zaten false positive olarak işaretlendi
            result['context_score'] = 0
            result['is_valid_category'] = False
            result['analysis_details']['confidence'] = 0
        elif negative_score > 0 and primary_found:
            # Hem anahtar kelime hem negatif pattern var
            result['context_score'] = negative_score
            result['is_valid_category'] = True
            result['analysis_details']['confidence'] = min(negative_score * 20, 100)  # Max %100
        elif primary_found and positive_score > 0:
            # Anahtar kelime var ama pozitif bağlamda
            result['context_score'] = positive_score
            result['is_valid_category'] = True
            result['analysis_details']['confidence'] = min(positive_score * 15, 80)  # Max %80
        elif primary_found:
            # Sadece anahtar kelime var, bağlam belirsiz
            result['context_score'] = len(primary_found)
            result['is_valid_category'] = len(primary_found) > 0
            result['analysis_details']['confidence'] = min(len(primary_found) * 10, 50)  # Max %50
        else:
            # Hiçbir anahtar kelime yok
            result['context_score'] = 0
            result['is_valid_category'] = False
            result['analysis_details']['confidence'] = 0
        
        return result

    def analyze_all_categories(self, text: str) -> Dict:
        """Tüm kategoriler için bağlamsal analiz"""
        
        results = {}
        
        for category in self.contextual_keywords.keys():
            results[category] = self.analyze_contextual_keywords(text, category)
        
        # En yüksek skorlu ve geçerli kategoriyi belirle
        valid_categories = {cat: data for cat, data in results.items() 
                          if data['is_valid_category'] and data['context_score'] > 0}
        
        if valid_categories:
            best_category = max(valid_categories.keys(), 
                              key=lambda x: valid_categories[x]['context_score'])
            
            return {
                'primary_category': best_category,
                'confidence': valid_categories[best_category]['analysis_details']['confidence'],
                'all_results': results,
                'summary': {
                    'total_valid_categories': len(valid_categories),
                    'excluded_categories': [cat for cat, data in results.items() 
                                          if data['analysis_details']['excluded_by_context']],
                    'best_match': {
                        'category': best_category,
                        'score': valid_categories[best_category]['context_score'],
                        'keywords': valid_categories[best_category]['found_keywords']
                    }
                }
            }
        else:
            return {
                'primary_category': None,
                'confidence': 0,
                'all_results': results,
                'summary': {
                    'total_valid_categories': 0,
                    'excluded_categories': [cat for cat, data in results.items() 
                                          if data['analysis_details']['excluded_by_context']],
                    'best_match': None
                }
            }

    def test_problematic_examples(self):
        """Problemli örnekleri test et"""
        
        test_cases = [
            {
                'text': "Bizim evin vazgeçilmezi, indirimdeyken stoklarız",
                'expected_category': None,  # Kargo problemi değil
                'reason': "vazgeçilmez kelimesindeki 'geç' false positive"
            },
            {
                'text': "vazgeçilmezimiz. İndirime girdikçe stokluyorum",
                'expected_category': None,
                'reason': "vazgeçilmez kelimesindeki 'geç' false positive"
            },
            {
                'text': "oğlum ek gıdaya geçtiğinden beri severek içiyoruz",
                'expected_category': None,
                'reason': "ek gıdaya geçti kelimesindeki 'geç' false positive"
            },
            {
                'text': "kargo çok geç geldi, 10 gün bekledim",
                'expected_category': 'kargo',
                'reason': "Gerçek kargo gecikmesi problemi"
            },
            {
                'text': "teslimat gecikmesi yaşadık, paket hasarlı geldi",
                'expected_category': 'kargo',
                'reason': "Gerçek kargo ve hasar problemi"
            }
        ]
        
        print("🔍 BAĞLAMSAL ANALİZ TEST SONUÇLARI:")
        print("="*60)
        
        for i, test in enumerate(test_cases, 1):
            result = self.analyze_all_categories(test['text'])
            
            predicted = result['primary_category']
            expected = test['expected_category']
            
            status = "✅ DOĞRU" if predicted == expected else "❌ YANLIŞ"
            
            print(f"\n{i}. TEST: {status}")
            print(f"   📝 Metin: \"{test['text'][:50]}...\"")
            print(f"   🎯 Beklenen: {expected}")
            print(f"   🤖 Tahmin: {predicted}")
            print(f"   📊 Güven: %{result['confidence']}")
            print(f"   💭 Sebep: {test['reason']}")
            
            if result['summary']['excluded_categories']:
                print(f"   🚫 Hariç tutulan: {result['summary']['excluded_categories']}")

def main():
    """Bağlamsal analiz demo"""
    
    analyzer = ContextualKeywordAnalyzer()
    
    print("🧠 BAĞLAMSAL KELİME ANALİZCİSİ")
    print("="*50)
    
    # Test problemli örnekleri
    analyzer.test_problematic_examples()
    
    print("\n" + "="*50)
    print("💡 ÇÖZELTİ ÖZETİ:")
    print("✅ 'vazgeçilmez' → Artık kargo problemi olarak algılanmıyor")
    print("✅ 'ek gıdaya geçti' → Artık kargo problemi olarak algılanmıyor") 
    print("✅ Gerçek kargo sorunları → Doğru şekilde tespit ediliyor")
    print("✅ Bağlamsal pattern matching → False positive'leri önlüyor")

if __name__ == "__main__":
    main() 