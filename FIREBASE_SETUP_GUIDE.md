# 🔥 FIREBASE RAG SİSTEMİ KURULUM REHBERİ

## 📋 Genel Bakış

Bu rehber, Trendyol yorum analiz sisteminizi **Google Firebase Firestore** ile entegre etmek için adım adım kurulum sürecini açıklar.

### 🎯 Ne Sağlar Firebase Entegrasyonu?

```python
✅ Gerçek zamanlı veritabanı (Firestore)
✅ Otomatik ölçeklendirme (serverless)
✅ Güçlü sorgu yetenekleri
✅ Real-time listeners
✅ Multi-platform sync
✅ Enterprise güvenlik
```

## 🚀 1. Firebase Proje Kurulumu

### **Adım 1.1: Firebase Console'da Proje Oluştur**

1. [Firebase Console](https://console.firebase.google.com) adresine gidin
2. **"Proje ekle"** butonuna tıklayın
3. Proje adı: `trendyol-comment-analysis`
4. Google Analytics'i etkinleştirin (opsiyonel)
5. **"Proje oluştur"** butonuna tıklayın

### **Adım 1.2: Firestore Database'i Etkinleştir**

1. Sol menüden **"Firestore Database"** seçin
2. **"Veritabanı oluştur"** butonuna tıklayın
3. **Güvenlik kuralları**: Test modunda başlayın
4. **Konum**: `europe-west3` (Frankfurt - Türkiye'ye yakın)
5. **"Bitti"** butonuna tıklayın

### **Adım 1.3: Service Account Oluştur**

1. **"Proje Ayarları"** > **"Hizmet Hesapları"**
2. **"Yeni özel anahtar oluştur"** butonuna tıklayın
3. **JSON** formatını seçin
4. Dosyayı indirin: `trendyol-firebase-service-account.json`
5. Dosyayı proje klasörünüze koyun

```bash
web-crawling/
├── firebase_rag_integration.py
├── trendyol-firebase-service-account.json  # Bu dosya
└── trendyol_comments.csv
```

## 🔧 2. Python Ortamı Hazırlığı

### **Adım 2.1: Gerekli Paketleri Yükle**

```bash
# Firebase bağımlılıklarını yükle
pip install -r requirements_firebase.txt

# Ana paketler
pip install firebase-admin google-cloud-firestore pandas
```

### **Adım 2.2: Environment Variables (Opsiyonel)**

```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\web-crawling\trendyol-firebase-service-account.json"

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/trendyol-firebase-service-account.json"
```

## 📊 3. Firestore Koleksiyon Yapısı

Firebase RAG sistemimiz şu koleksiyonları kullanır:

### **3.1: `trendyol_comments` Koleksiyonu**
```javascript
{
  "comment_hash": "abc123...",
  "user": "Kullanıcı Adı",
  "date": "2024-01-15",
  "comment": "Ürün çok güzel, beğendim...",
  "uploaded_at": Timestamp,
  "processed": false,
  "analysis_completed": false
}
```

### **3.2: `comment_analysis` Koleksiyonu**
```javascript
{
  "comment_id": "doc_ref_id",
  "comment_hash": "abc123...",
  "sentiment_analysis": {
    "category_analysis": {...},
    "total_comments": 100
  },
  "priority_analysis": {
    "critical_issues": {...}
  },
  "analyzed_at": Timestamp,
  "version": "1.0"
}
```

### **3.3: `rag_knowledge` Koleksiyonu**
```javascript
{
  "category": "kargo",
  "problem_description": "Kargo gecikmesi ve teslimat sorunları",
  "solution": "Alternatif kargo firmaları ile anlaşma yapın...",
  "source": "internal_policy",
  "created_at": Timestamp,
  "usage_count": 0,
  "effectiveness_score": 0.0,
  "tags": ["kargo", "teslimat"]
}
```

### **3.4: `realtime_logs` Koleksiyonu**
```javascript
{
  "timestamp": Timestamp,
  "event_type": "comment_processed",
  "details": {...},
  "system_status": "active"
}
```

## 🎯 4. Sistem Kullanımı

### **Adım 4.1: Firebase RAG Sistemini Başlat**

```python
# Firebase service account ile
firebase_rag = FirebaseRAGSystem('trendyol-firebase-service-account.json')

# Environment variable ile
firebase_rag = FirebaseRAGSystem()  # GOOGLE_APPLICATION_CREDENTIALS kullanır
```

### **Adım 4.2: CSV Verilerini Firestore'a Yükle**

```python
# trendyol_comments.csv dosyasını yükle
uploaded_count = firebase_rag.upload_csv_to_firestore('trendyol_comments.csv')
print(f"✅ {uploaded_count} yorum Firestore'a yüklendi")
```

### **Adım 4.3: Yorumları Analiz Et**

```python
# İşlenmemiş yorumları analiz et
processed_count = firebase_rag.process_unanalyzed_comments()
print(f"🔬 {processed_count} yorum analiz edildi")
```

### **Adım 4.4: RAG Bilgi Tabanını Kur**

```python
# Örnek bilgi tabanını oluştur
firebase_rag.setup_sample_knowledge_base()

# Manuel bilgi ekle
firebase_rag.add_knowledge_base_entry(
    category="kargo",
    problem="Express teslimat gecikmesi",
    solution="Aynı gün teslimat seçeneği sunun, premium kargo ile anlaşma yapın",
    source="operations_team"
)
```

### **Adım 4.5: RAG Arama Sistemi**

```python
# Bilgi tabanında arama
results = firebase_rag.search_knowledge_base(
    query="kargo problemi nasıl çözülür",
    category="kargo",  # Opsiyonel filtreleme
    limit=5
)

for result in results:
    print(f"📝 Çözüm: {result['solution']}")
    print(f"📊 Relevance: {result['relevance_score']:.2f}")
```

## 📈 5. Gerçek Zamanlı İzleme

### **5.1: Real-time Listeners (Gelişmiş)**

```python
def on_new_comment(doc_snapshot, changes, read_time):
    """Yeni yorum geldiğinde otomatik çalış"""
    for change in changes:
        if change.type.name == 'ADDED':
            comment_data = change.document.to_dict()
            print(f"🆕 Yeni yorum: {comment_data['comment'][:50]}...")
            
            # Otomatik analiz başlat
            # analyze_new_comment(comment_data)

# Listener kurulumu
firebase_rag.db.collection('trendyol_comments').on_snapshot(on_new_comment)
```

### **5.2: Otomatik Monitoring**

```python
# Periyodik sistem kontrolü
import schedule
import time

def check_system_health():
    insights = firebase_rag.get_real_time_insights()
    
    if insights['urgent_count'] > 0:
        print(f"🚨 {insights['urgent_count']} acil kategori tespit edildi!")
        # Send notification

# Her 5 dakikada bir kontrol et
schedule.every(5).minutes.do(check_system_health)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 🔒 6. Güvenlik Ayarları

### **6.1: Firestore Güvenlik Kuralları**

```javascript
// Firestore Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Yorumlar - okuma/yazma izni
    match /trendyol_comments/{document} {
      allow read, write: if request.auth != null;
    }
    
    // Analiz sonuçları - sadece okuma
    match /comment_analysis/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                   request.auth.token.admin == true;
    }
    
    // RAG bilgi tabanı - admin only
    match /rag_knowledge/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                   request.auth.token.admin == true;
    }
  }
}
```

### **6.2: API Key Güvenliği**

```python
# Service account güvenli saklama
import os
from pathlib import Path

# Config dosyası
CONFIG = {
    'firebase_credentials': os.getenv('FIREBASE_CREDENTIALS_PATH', 
                                    'trendyol-firebase-service-account.json'),
    'project_id': 'trendyol-comment-analysis',
    'database_url': 'https://trendyol-comment-analysis.firebaseio.com'
}

# Credentials dosyası varlık kontrolü
credentials_path = Path(CONFIG['firebase_credentials'])
if not credentials_path.exists():
    raise FileNotFoundError(f"Firebase credentials bulunamadı: {credentials_path}")
```

## 📊 7. Performans Optimizasyonu

### **7.1: Firestore İndeksleme**

Firebase Console > Firestore > İndeksler sekmesinde şu indeksleri oluşturun:

```javascript
// Composite index for efficient querying
Collection: trendyol_comments
Fields: processed (Ascending), uploaded_at (Descending)

Collection: comment_analysis  
Fields: analyzed_at (Descending), priority_analysis.urgent_count (Ascending)

Collection: rag_knowledge
Fields: category (Ascending), tags (Array), created_at (Descending)
```

### **7.2: Batch Operations**

```python
# Toplu işlemler için batch kullanın
batch = firebase_rag.db.batch()

for comment in comments_to_process:
    doc_ref = firebase_rag.db.collection('trendyol_comments').document()
    batch.set(doc_ref, comment)

# Tek seferde commit
batch.commit()
print(f"✅ {len(comments_to_process)} yorum toplu olarak eklendi")
```

### **7.3: Caching Strategy**

```python
from functools import lru_cache
import json

@lru_cache(maxsize=100)
def cached_knowledge_search(query: str, category: str = None):
    """Cache'lenmiş bilgi tabanı araması"""
    return firebase_rag.search_knowledge_base(query, category)

# Memory-based cache
class FirebaseCache:
    def __init__(self, ttl: int = 300):  # 5 dakika TTL
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key: str, value):
        self.cache[key] = (value, time.time())
```

## 🚀 8. Deployment ve Production

### **8.1: Environment Yapılandırması**

```python
# config.py
import os

class Config:
    # Firebase
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'trendyol-comment-analysis')
    
    # System
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))  # 5 dakika
    
    # Features
    ENABLE_REALTIME_MONITORING = os.getenv('ENABLE_REALTIME', 'true').lower() == 'true'
    ENABLE_AUTO_ANALYSIS = os.getenv('ENABLE_AUTO_ANALYSIS', 'true').lower() == 'true'

# Production kullanımı
firebase_rag = FirebaseRAGSystem(Config.FIREBASE_CREDENTIALS)
```

### **8.2: Docker Container**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Requirements
COPY requirements_firebase.txt .
RUN pip install -r requirements_firebase.txt

# App files
COPY . .

# Firebase credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-credentials.json

# Run
CMD ["python", "firebase_rag_integration.py"]
```

### **8.3: Cloud Run Deployment**

```bash
# Google Cloud Run'da deploy
gcloud run deploy trendyol-rag \
    --source . \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-credentials.json
```

## 🧪 9. Test ve Doğrulama

### **9.1: Unit Tests**

```python
import unittest
from firebase_rag_integration import FirebaseRAGSystem

class TestFirebaseRAG(unittest.TestCase):
    
    def setUp(self):
        # Test Firebase project
        self.firebase_rag = FirebaseRAGSystem('test-credentials.json')
    
    def test_csv_upload(self):
        """CSV yükleme testi"""
        result = self.firebase_rag.upload_csv_to_firestore('test_comments.csv')
        self.assertGreater(result, 0)
    
    def test_knowledge_search(self):
        """RAG arama testi"""
        results = self.firebase_rag.search_knowledge_base('kargo sorunu')
        self.assertIsInstance(results, list)
    
    def test_analysis_pipeline(self):
        """Analiz pipeline testi"""
        processed = self.firebase_rag.process_unanalyzed_comments()
        self.assertGreaterEqual(processed, 0)

if __name__ == '__main__':
    unittest.main()
```

### **9.2: Integration Tests**

```python
# test_integration.py
def test_end_to_end_workflow():
    """Tam iş akışı testi"""
    
    # 1. CSV yükle
    firebase_rag.upload_csv_to_firestore('sample_comments.csv')
    
    # 2. Analiz et
    firebase_rag.process_unanalyzed_comments()
    
    # 3. RAG ara
    results = firebase_rag.search_knowledge_base('teslimat sorunu')
    
    # 4. Insight'ları al
    insights = firebase_rag.get_real_time_insights()
    
    assert len(results) > 0
    assert insights['total_comments_24h'] >= 0
```

## 🎯 10. Kullanım Senaryoları

### **Senaryo 1: Günlük Rutin**
```bash
# Her sabah çalıştırılacak script
python firebase_rag_integration.py --mode daily_routine
```

### **Senaryo 2: Acil Durum Monitoring**
```bash
# Sürekli izleme modu
python firebase_rag_integration.py --mode realtime_monitoring
```

### **Senaryo 3: Rapor Oluşturma**
```bash
# Haftalık rapor
python firebase_rag_integration.py --mode weekly_report
```

---

## 🏆 Sonuç

Bu Firebase entegrasyonu ile artık:

✅ **Gerçek zamanlı veritabanı** - Mock veriler yerine canlı Firestore
✅ **Ölçeklenebilir mimari** - Otomatik scaling ve performance
✅ **Enterprise güvenlik** - Google Cloud güvenlik standartları
✅ **Global erişim** - Multi-region deployment imkanı
✅ **Real-time sync** - Anlık veri güncellemeleri

**🚀 Artık sisteminiz enterprise-ready ve production-grade!** 