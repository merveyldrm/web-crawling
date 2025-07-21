import csv
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import re
from datetime import datetime, timedelta

class PriorityAnalyzer:
    def __init__(self):
        # Öncelik kategorileri ve iş etkisi ağırlıkları
        self.priority_categories = {
            'kargo': {
                'business_impact': 9,  # 1-10 skala (10 en yüksek)
                'urgency_multiplier': 1.2,
                'description': 'Teslimat ve lojistik sorunları',
                'critical_keywords': ['hasarlı', 'kırık', 'geç', 'gelmedi', 'kayıp', 'zarar', 'bozuk paket'],
                'department': 'Lojistik'
            },
            'kalite': {
                'business_impact': 10,
                'urgency_multiplier': 1.5,
                'description': 'Ürün kalitesi ve üretim sorunları',
                'critical_keywords': ['bozuk', 'defolu', 'kırık', 'çalışmıyor', 'sahte', 'taklit', 'berbat'],
                'department': 'Kalite Kontrol'
            },
            'beden_uyum': {
                'business_impact': 8,
                'urgency_multiplier': 1.1,
                'description': 'Beden ve uyum sorunları (iade riski yüksek)',
                'critical_keywords': ['hiç uymadı', 'çok büyük', 'çok küçük', 'berbat kalıp', 'iade'],
                'department': 'Ürün Yönetimi'
            },
            'musteri_hizmeti': {
                'business_impact': 7,
                'urgency_multiplier': 1.3,
                'description': 'Müşteri hizmetleri ve destek sorunları',
                'critical_keywords': ['kaba', 'ilgisiz', 'çözüm yok', 'dönmüyor', 'saygısız'],
                'department': 'Müşteri Hizmetleri'
            },
            'fiyat': {
                'business_impact': 6,
                'urgency_multiplier': 0.8,
                'description': 'Fiyatlandırma ve değer algısı',
                'critical_keywords': ['çok pahalı', 'değmez', 'fahiş', 'aşırı', 'hırsızlık'],
                'department': 'Fiyatlandırma'
            },
            'urun_ozellikleri': {
                'business_impact': 8,
                'urgency_multiplier': 1.2,
                'description': 'Ürün fonksiyonelliği ve performans',
                'critical_keywords': ['çalışmıyor', 'bozuk', 'işe yaramaz', 'anlattığı gibi değil'],
                'department': 'Ürün Geliştirme'
            },
            'renk_gorsel': {
                'business_impact': 5,
                'urgency_multiplier': 0.9,
                'description': 'Görsel uyumsuzluk ve renk sorunları',
                'critical_keywords': ['hiç benzemez', 'bambaşka', 'aldatmaca', 'yanıltıcı'],
                'department': 'E-ticaret'
            }
        }
        
        # Olumsuzluk derecesi hesaplama
        self.negativity_indicators = {
            'extreme': {
                'keywords': ['berbat', 'rezalet', 'çöp', 'hiç beğenmedim', 'pişman oldum', 'aldatmaca', 'hırsızlık'],
                'score': 10,
                'description': 'Aşırı olumsuz - acil müdahale'
            },
            'severe': {
                'keywords': ['kötü', 'berbat', 'sorunlu', 'memnun değilim', 'beğenmedim', 'iade'],
                'score': 8,
                'description': 'Şiddetli olumsuz - hızlı çözüm gerekli'
            },
            'moderate': {
                'keywords': ['idare eder', 'orta', 'beklediğim gibi değil', 'eksik', 'vasat'],
                'score': 5,
                'description': 'Orta seviye olumsuz - takip gerekli'
            },
            'mild': {
                'keywords': ['fena değil', 'normal', 'olabilir'],
                'score': 3,
                'description': 'Hafif olumsuz - gözlem altında'
            }
        }
        
        # Aciliyet göstergeleri
        self.urgency_indicators = {
            'volume_based': {
                'high_volume_threshold': 10,  # Bu kategoride 10+ şikayet varsa acil
                'multiplier': 1.3
            },
            'time_based': {
                'recent_days': 7,  # Son 7 gün
                'multiplier': 1.2
            },
            'repeat_customer': {
                'multiplier': 1.4  # Aynı müşterinin tekrar şikayet etmesi
            }
        }

    def calculate_negativity_score(self, comment_text: str) -> Dict:
        """Yorumun olumsuzluk skorunu hesapla"""
        text_lower = comment_text.lower()
        
        # Her seviye için skorları hesapla
        level_scores = {}
        for level, data in self.negativity_indicators.items():
            found_keywords = [kw for kw in data['keywords'] if kw in text_lower]
            if found_keywords:
                level_scores[level] = {
                    'score': data['score'],
                    'keywords': found_keywords,
                    'description': data['description']
                }
        
        # En yüksek seviyeyi belirle
        if level_scores:
            highest_level = max(level_scores.keys(), key=lambda x: level_scores[x]['score'])
            return {
                'negativity_level': highest_level,
                'negativity_score': level_scores[highest_level]['score'],
                'found_keywords': level_scores[highest_level]['keywords'],
                'description': level_scores[highest_level]['description'],
                'all_levels': level_scores
            }
        else:
            return {
                'negativity_level': 'none',
                'negativity_score': 0,
                'found_keywords': [],
                'description': 'Olumsuzluk tespit edilmedi',
                'all_levels': {}
            }

    def calculate_priority_score(self, category: str, negativity_data: Dict, 
                               comment_count: int, recent_count: int) -> Dict:
        """Öncelik skorunu hesapla"""
        if category not in self.priority_categories:
            return {'priority_score': 0, 'details': 'Bilinmeyen kategori'}
        
        cat_data = self.priority_categories[category]
        
        # Temel skor hesaplama
        base_score = cat_data['business_impact']  # 1-10
        negativity_score = negativity_data['negativity_score']  # 0-10
        urgency_multiplier = cat_data['urgency_multiplier']  # 0.8-1.5
        
        # Hacim bazlı aciliyet
        volume_multiplier = 1.0
        if comment_count >= self.urgency_indicators['volume_based']['high_volume_threshold']:
            volume_multiplier = self.urgency_indicators['volume_based']['multiplier']
        
        # Zaman bazlı aciliyet (son 7 gün)
        time_multiplier = 1.0
        if recent_count > 0:
            time_multiplier = self.urgency_indicators['time_based']['multiplier']
        
        # Final skor hesaplama
        priority_score = (
            (base_score * 0.4) +  # İş etkisi %40
            (negativity_score * 0.6)  # Olumsuzluk %60
        ) * urgency_multiplier * volume_multiplier * time_multiplier
        
        # 100 üzerinden skala
        priority_score = min(priority_score * 10, 100)
        
        return {
            'priority_score': round(priority_score, 1),
            'business_impact': base_score,
            'negativity_impact': negativity_score,
            'urgency_multiplier': urgency_multiplier,
            'volume_multiplier': volume_multiplier,
            'time_multiplier': time_multiplier,
            'comment_count': comment_count,
            'recent_count': recent_count,
            'department': cat_data['department'],
            'description': cat_data['description']
        }

    def analyze_critical_issues(self, comments: List[Dict], 
                              sentiment_analysis: Dict) -> Dict:
        """Kritik sorunları analiz et ve önceliklendir"""
        
        print("🚨 Kritik sorun analizi başlıyor...")
        
        critical_issues = {}
        category_analysis = sentiment_analysis.get('category_analysis', {})
        
        # Her kategori için analiz
        for category, data in category_analysis.items():
            if category not in self.priority_categories:
                continue
                
            negative_comments = data.get('negative', [])
            if not negative_comments:
                continue
            
            print(f"🔍 {category} kategorisi analiz ediliyor...")
            
            # Negatif yorumları detaylı analiz et
            issue_details = []
            total_negativity = 0
            critical_count = 0
            recent_count = 0
            
            # Son 7 gün için tarih kontrolü
            recent_date = datetime.now() - timedelta(days=7)
            
            for comment_data in negative_comments:
                comment_text = comment_data.get('comment', '')
                comment_date = comment_data.get('date', '')
                
                # Olumsuzluk skorunu hesapla
                negativity_data = self.calculate_negativity_score(comment_text)
                total_negativity += negativity_data['negativity_score']
                
                # Kritik kelime kontrolü
                critical_keywords = []
                for keyword in self.priority_categories[category]['critical_keywords']:
                    if keyword in comment_text.lower():
                        critical_keywords.append(keyword)
                        critical_count += 1
                
                # Son 7 gün kontrolü (basit string kontrolü)
                is_recent = False
                try:
                    # Farklı tarih formatlarını dene
                    for date_format in ['%d %B %Y', '%d.%m.%Y', '%Y-%m-%d']:
                        try:
                            comment_dt = datetime.strptime(comment_date, date_format)
                            if comment_dt >= recent_date:
                                is_recent = True
                                recent_count += 1
                            break
                        except:
                            continue
                except:
                    pass
                
                issue_details.append({
                    'comment': comment_text[:200] + '...',
                    'user': comment_data.get('user', 'Anonim'),
                    'date': comment_date,
                    'negativity_data': negativity_data,
                    'critical_keywords': critical_keywords,
                    'is_recent': is_recent
                })
            
            # Ortalama olumsuzluk skoru
            avg_negativity = total_negativity / len(negative_comments) if negative_comments else 0
            
            # Öncelik skorunu hesapla
            priority_data = self.calculate_priority_score(
                category,
                {'negativity_score': avg_negativity},
                len(negative_comments),
                recent_count
            )
            
            critical_issues[category] = {
                'priority_score': priority_data['priority_score'],
                'priority_details': priority_data,
                'total_negative_comments': len(negative_comments),
                'average_negativity': round(avg_negativity, 1),
                'critical_keyword_mentions': critical_count,
                'recent_complaints': recent_count,
                'issue_details': issue_details[:5],  # En fazla 5 örnek
                'all_issue_details': issue_details,
                'category_info': self.priority_categories[category]
            }
        
        # Öncelik sırasına göre sırala
        sorted_issues = dict(sorted(
            critical_issues.items(),
            key=lambda x: x[1]['priority_score'],
            reverse=True
        ))
        
        return {
            'critical_issues': sorted_issues,
            'summary': self._generate_priority_summary(sorted_issues),
            'action_plan': self._generate_action_plan(sorted_issues)
        }

    def _generate_priority_summary(self, sorted_issues: Dict) -> Dict:
        """Öncelik özetini oluştur"""
        if not sorted_issues:
            return {'message': 'Kritik seviyede sorun tespit edilmedi'}
        
        summary = {
            'total_critical_categories': len(sorted_issues),
            'highest_priority': {},
            'urgent_categories': [],
            'moderate_categories': [],
            'low_priority_categories': []
        }
        
        # En yüksek öncelik
        highest_cat = list(sorted_issues.keys())[0]
        summary['highest_priority'] = {
            'category': highest_cat,
            'score': sorted_issues[highest_cat]['priority_score'],
            'description': sorted_issues[highest_cat]['category_info']['description']
        }
        
        # Kategorileri öncelik seviyesine göre grupla
        for category, data in sorted_issues.items():
            score = data['priority_score']
            
            if score >= 80:
                summary['urgent_categories'].append({
                    'category': category,
                    'score': score,
                    'comment_count': data['total_negative_comments']
                })
            elif score >= 60:
                summary['moderate_categories'].append({
                    'category': category,
                    'score': score,
                    'comment_count': data['total_negative_comments']
                })
            else:
                summary['low_priority_categories'].append({
                    'category': category,
                    'score': score,
                    'comment_count': data['total_negative_comments']
                })
        
        return summary

    def _generate_action_plan(self, sorted_issues: Dict) -> List[Dict]:
        """Aksiyon planı oluştur"""
        action_plan = []
        
        for category, data in sorted_issues.items():
            score = data['priority_score']
            
            # Aciliyet seviyesini belirle
            if score >= 80:
                urgency = 'ACİL - 24 saat içinde'
                action_type = 'Kritik Müdahale'
            elif score >= 60:
                urgency = 'YÜKSEK - 3 gün içinde'
                action_type = 'Hızlı Çözüm'
            elif score >= 40:
                urgency = 'ORTA - 1 hafta içinde'
                action_type = 'Planlı İyileştirme'
            else:
                urgency = 'DÜŞÜK - 1 ay içinde'
                action_type = 'Uzun Vadeli Plan'
            
            # Önerilen aksiyonlar
            suggested_actions = self._get_category_specific_actions(category, data)
            
            action_plan.append({
                'category': category,
                'priority_score': score,
                'urgency': urgency,
                'action_type': action_type,
                'responsible_department': data['category_info']['department'],
                'description': data['category_info']['description'],
                'problem_count': data['total_negative_comments'],
                'suggested_actions': suggested_actions,
                'key_issues': [detail['critical_keywords'] for detail in data['issue_details'] if detail['critical_keywords']]
            })
        
        return action_plan

    def _get_category_specific_actions(self, category: str, data: Dict) -> List[str]:
        """Kategoriye özel önerilen aksiyonlar"""
        actions = {
            'kargo': [
                'Kargo firması ile acil toplantı',
                'Paketleme sürecini gözden geçir',
                'Alternatif kargo seçenekleri değerlendir',
                'Hasar raporlama sistemini iyileştir'
            ],
            'kalite': [
                'Kalite kontrol sürecini durdur ve incele',
                'Tedarikçi kalite denetimi',
                'Üretim sürecinde ani kalite kontrolü',
                'Kusurlu ürünlerin geri çağırılması'
            ],
            'beden_uyum': [
                'Beden tablosu güncelleme',
                'Ürün fotoğraflarını yeniden çek',
                'Model ölçüleri doğrulaması',
                'İade politikası esnekleştirme'
            ],
            'musteri_hizmeti': [
                'Müşteri hizmetleri ekibine acil eğitim',
                'Yanıt sürelerini iyileştir',
                'Şikayet takip sistemini güçlendir',
                'Müşteri memnuniyeti anketleri'
            ],
            'fiyat': [
                'Rakip fiyat analizi',
                'Fiyatlandırma stratejisi gözden geçirme',
                'Değer önerisi iyileştirme',
                'İndirim ve kampanya planlaması'
            ],
            'urun_ozellikleri': [
                'Ürün açıklamalarını güncelle',
                'Fonksiyon testlerini artır',
                'Kullanım kılavuzu iyileştirme',
                'Ürün geliştirme sürecini gözden geçir'
            ],
            'renk_gorsel': [
                'Ürün fotoğrafçılığını iyileştir',
                'Renk standardizasyonu',
                'Görsel tutarlılık kontrolü',
                'Stüdyo ışıklandırması ayarları'
            ]
        }
        
        return actions.get(category, ['Genel iyileştirme önerileri gerekli'])

    def generate_priority_report(self, priority_analysis: Dict) -> str:
        """Öncelik raporu oluştur"""
        report = []
        report.append("🚨 OLUMSUZLUK DERECESİ VE ÖNCELİKLENDİRME RAPORU")
        report.append("=" * 80)
        
        summary = priority_analysis.get('summary', {})
        critical_issues = priority_analysis.get('critical_issues', {})
        action_plan = priority_analysis.get('action_plan', [])
        
        # Özet
        if 'message' in summary:
            report.append(f"\n✅ {summary['message']}")
            return '\n'.join(report)
        
        report.append(f"\n📊 ÖZET BİLGİLER")
        report.append(f"   • Kritik Kategori Sayısı: {summary['total_critical_categories']}")
        
        # En yüksek öncelik
        highest = summary.get('highest_priority', {})
        if highest:
            report.append(f"\n🔥 EN YÜKSEK ÖNCELİK")
            report.append(f"   📋 Kategori: {highest['category'].upper()}")
            report.append(f"   📊 Öncelik Skoru: {highest['score']}/100")
            report.append(f"   📝 Açıklama: {highest['description']}")
        
        # Acil kategoriler
        urgent = summary.get('urgent_categories', [])
        if urgent:
            report.append(f"\n🚨 ACİL MÜDAHALE GEREKTİREN KATEGORILER (80+ skor)")
            for cat in urgent:
                report.append(f"   🔴 {cat['category'].upper()}: {cat['score']}/100 ({cat['comment_count']} şikayet)")
        
        # Yüksek öncelik
        moderate = summary.get('moderate_categories', [])
        if moderate:
            report.append(f"\n⚠️ YÜKSEK ÖNCELİK KATEGORILER (60-79 skor)")
            for cat in moderate:
                report.append(f"   🟡 {cat['category'].upper()}: {cat['score']}/100 ({cat['comment_count']} şikayet)")
        
        # Detaylı analiz
        report.append(f"\n" + "=" * 80)
        report.append(f"📋 DETAYLI SORUN ANALİZİ")
        report.append(f"=" * 80)
        
        for category, data in critical_issues.items():
            score = data['priority_score']
            
            # Renk kodları
            if score >= 80:
                emoji = "🔴"
                urgency = "ACİL"
            elif score >= 60:
                emoji = "🟡"
                urgency = "YÜKSEK"
            else:
                emoji = "🔵"
                urgency = "ORTA"
            
            report.append(f"\n{emoji} {category.upper()} - {urgency} ÖNCELİK")
            report.append(f"   📊 Öncelik Skoru: {score}/100")
            report.append(f"   🏢 Sorumlu Departman: {data['category_info']['department']}")
            report.append(f"   💬 Toplam Negatif Yorum: {data['total_negative_comments']}")
            report.append(f"   📈 Ortalama Olumsuzluk: {data['average_negativity']}/10")
            report.append(f"   🔥 Kritik Kelime Sayısı: {data['critical_keyword_mentions']}")
            report.append(f"   📅 Son 7 Gün İçindeki Şikayet: {data['recent_complaints']}")
            
            # Örnek problemler
            if data['issue_details']:
                report.append(f"   📝 Örnek Problemler:")
                for i, issue in enumerate(data['issue_details'][:3], 1):
                    report.append(f"      {i}. \"{issue['comment'][:100]}...\"")
                    if issue['critical_keywords']:
                        report.append(f"         🔍 Kritik: {', '.join(issue['critical_keywords'])}")
        
        # Aksiyon Planı
        report.append(f"\n" + "=" * 80)
        report.append(f"🎯 ÖNCELİKLENDİRİLMİŞ AKSİYON PLANI")
        report.append(f"=" * 80)
        
        for i, action in enumerate(action_plan, 1):
            if action['priority_score'] >= 80:
                emoji = "🔴"
            elif action['priority_score'] >= 60:
                emoji = "🟡"
            else:
                emoji = "🔵"
            
            report.append(f"\n{emoji} AKSİYON {i}: {action['category'].upper()}")
            report.append(f"   ⏰ Aciliyet: {action['urgency']}")
            report.append(f"   🎯 Aksiyon Tipi: {action['action_type']}")
            report.append(f"   🏢 Sorumlu: {action['responsible_department']}")
            report.append(f"   📊 Problem Sayısı: {action['problem_count']}")
            
            report.append(f"   📋 Önerilen Aksiyonlar:")
            for j, suggestion in enumerate(action['suggested_actions'][:3], 1):
                report.append(f"      {j}. {suggestion}")
        
        return '\n'.join(report)

    def save_priority_analysis(self, priority_analysis: Dict, filename: str = 'priority_analysis.json'):
        """Öncelik analizini kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(priority_analysis, f, ensure_ascii=False, indent=2, default=str)
            print(f"📁 Öncelik analizi {filename} dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")

    def save_priority_report(self, priority_analysis: Dict, filename: str = 'priority_report.txt'):
        """Öncelik raporunu metin olarak kaydet"""
        try:
            report = self.generate_priority_report(priority_analysis)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Öncelik raporu {filename} dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Rapor kaydetme hatası: {e}")


def main():
    """Öncelik analizi demo"""
    from advanced_comment_analyzer import AdvancedCommentAnalyzer
    
    print("🚨 ÖNCELİKLENDİRME SİSTEMİ DEMO")
    print("=" * 50)
    
    # Analizcileri başlat
    comment_analyzer = AdvancedCommentAnalyzer()
    priority_analyzer = PriorityAnalyzer()
    
    # Yorumları yükle
    comments = comment_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    if not comments:
        print("❌ Yorum yüklenemedi!")
        return
    
    # Sentiment analizi yap
    print("🎭 Sentiment analizi yapılıyor...")
    sentiment_analysis = comment_analyzer.analyze_all_comments(comments)
    
    # Öncelik analizi yap
    print("🚨 Kritik sorun analizi yapılıyor...")
    priority_analysis = priority_analyzer.analyze_critical_issues(comments, sentiment_analysis)
    
    # Raporu göster
    report = priority_analyzer.generate_priority_report(priority_analysis)
    print("\n" + report)
    
    # Dosyaları kaydet
    priority_analyzer.save_priority_analysis(priority_analysis, 'priority_analysis.json')
    priority_analyzer.save_priority_report(priority_analysis, 'priority_report.txt')
    
    print(f"\n✅ Öncelik analizi tamamlandı!")
    print(f"📁 Detaylı analiz: priority_analysis.json")
    print(f"📄 Rapor: priority_report.txt")


if __name__ == "__main__":
    main() 