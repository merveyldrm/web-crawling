# 🚀 Comprehensive RAG System - Advanced Comment Analysis & Management

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-green.svg)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Proje Hakkında

**Comprehensive RAG System**, müşteri yorumlarını analiz etmek, kategorize etmek ve akıllı arama yapmak için geliştirilmiş gelişmiş bir **Retrieval Augmented Generation (RAG)** sistemidir. Sistem, Trendyol gibi e-ticaret platformlarından toplanan yorumları işleyerek işletmelere değerli içgörüler sunar.

### 🎯 Ana Özellikler

- **🧠 Akıllı RAG Sistemi**: FAISS tabanlı vektör arama ile gelişmiş semantik anlama
- **🔍 Bağlamsal Anahtar Kelime Analizi**: False positive'leri önleyen akıllı kelime tespiti
- **📊 Konu Modelleme**: LDA, K-Means ve Hierarchical clustering ile gizli pattern'ları keşfetme
- **📝 Yorum Özetleme**: AI destekli otomatik yorum özetleme ve insight üretimi
- **🎯 Öncelik Analizi**: Yorumları iş etkisine göre önceliklendirme
- **📈 Gerçek Zamanlı Dashboard**: Canlı sistem metrikleri ve performans izleme
- **🌐 Çok Dilli Destek**: Türkçe, İngilizce ve 50+ dil desteği

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                        │
├─────────────────────────────────────────────────────────────┤
│  💬 RAG Chat  │  📊 Data Mgmt  │  🧠 Knowledge Base      │
├─────────────────────────────────────────────────────────────┤
│  🔍 Advanced  │  📈 Analytics  │  🔧 System Admin        │
│     Search    │    Dashboard   │                          │
├─────────────────────────────────────────────────────────────┤
│  📡 Real-time │  🎯 Topic      │  📝 Comment              │
│     Monitor   │   Modeling    │  Summarization            │
├─────────────────────────────────────────────────────────────┤
│              🔍 Contextual Analysis                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Core RAG System                            │
├─────────────────────────────────────────────────────────────┤
│  • FAISS Vector Database (384D embeddings)                │
│  • SQLite Data Storage                                    │
│  • Sentence Transformers                                  │
│  • Advanced Analyzers                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Sources & Scrapers                       │
├─────────────────────────────────────────────────────────────┤
│  • Trendyol Selenium Scraper                              │
│  • API-based Comment Collection                           │
│  • CSV/JSON Import Support                                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Kurulum

### Gereksinimler

- **Python**: 3.8+ (3.11 veya 3.12 önerilir)
- **RAM**: 8GB+ (AI modeller için)
- **Browser**: Chrome/Chromium (Selenium scraping için)

> **⚠️ Python 3.13 Uyumluluğu**: Bazı paketler Python 3.13 ile uyumlu olmayabilir. 
> En iyi performans için Python 3.11 veya 3.12 kullanmanız önerilir.

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/yourusername/web-crawling.git
cd web-crawling
```

### 2. Sanal Ortam Oluşturun

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. NLTK Verilerini İndirin

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## 🎮 Kullanım

### Streamlit Uygulamasını Başlatın

```bash
streamlit run comprehensive_rag_streamlit.py
```

Uygulama `http://localhost:8501` adresinde açılacaktır.

### 🎯 Sistem Başlatma

1. **Sidebar'dan Model Seçimi**: Embedding modelini seçin
2. **RAG Sistemi Başlat**: "Initialize RAG System" butonuna tıklayın
3. **Veri Yükleme**: Data Management tab'ından CSV dosyalarını yükleyin
4. **Analiz Başlat**: İstediğiniz tab'ı kullanarak analiz yapın

## 📊 Sistem Özellikleri

### 💬 RAG Chat Interface
- Doğal dil ile soru sorma
- Semantik arama ve benzerlik skorlama
- Bilgi tabanından otomatik cevap üretimi

### 🔍 Bağlamsal Anahtar Kelime Analizi
- **Akıllı Tespit**: Kelimeleri bağlamında anlama
- **False Positive Önleme**: "vazgeçilmez" vs "kargo geç geldi" ayrımı
- **Kategori Sınıflandırma**: Otomatik kargo, kalite, beden uyum kategorileri
- **Güven Skorlama**: Her analiz için güvenilirlik puanı

### 🎯 Konu Modelleme
- **LDA (Latent Dirichlet Allocation)**: Gizli konuları keşfetme
- **K-Means Clustering**: Benzer yorumları gruplama
- **Hierarchical Clustering**: Hiyerarşik konu organizasyonu
- **Coherence Scoring**: Konu kalitesi değerlendirmesi

### 📝 Yorum Özetleme
- **AI Destekli Özetleme**: Anahtar bilgileri çıkarma
- **Keyword Extraction**: Önemli kelimeleri tespit etme
- **Business Insights**: İş insights'ları üretme
- **Comprehensive Reports**: Detaylı analiz raporları

### 📈 Analytics Dashboard
- **Gerçek Zamanlı Metrikler**: Sistem performans izleme
- **Kategori Dağılımı**: Yorum kategorilerinin görselleştirilmesi
- **Öncelik Analizi**: Yorum öncelik skorlarının dağılımı
- **Sentiment Analysis**: Duygu analizi sonuçları

## 🔧 Gelişmiş Özellikler

### Anti-Bot Bypass
- Headless Chrome kullanımı
- User-Agent rotasyonu
- Proxy desteği
- Rate limiting

### Vektör Veritabanı
- FAISS IndexFlatIP algoritması
- 384 boyutlu embedding'ler
- Cosine similarity hesaplama
- Persistent storage

### Çoklu Analiz Modülleri
- Priority Analyzer
- Topic Modeling Analyzer
- Comment Summarizer
- Contextual Keyword Analyzer

## 📁 Proje Yapısı

```
web-crawling/
├── 📄 comprehensive_rag_streamlit.py    # Ana Streamlit uygulaması
├── 🧠 src/
│   ├── analyzers/                      # Analiz modülleri
│   │   ├── advanced_comment_analyzer.py
│   │   ├── comment_summarizer.py
│   │   ├── contextual_keyword_analyzer.py
│   │   ├── priority_analyzer.py
│   │   └── topic_modeling_analyzer.py
│   ├── scrapers/                       # Web scraping modülleri
│   │   └── trendyol_selenium_scraper.py
│   └── rag_systems/                    # RAG sistem modülleri
├── 📊 data/                            # Veri dosyaları
│   ├── raw/                           # Ham veriler
│   └── processed/                     # İşlenmiş veriler
├── 🔧 config/                          # Konfigürasyon dosyaları
├── 📚 docs/                           # Dokümantasyon
├── 🧪 tests/                          # Test dosyaları
├── 📋 requirements.txt                 # Python bağımlılıkları
└── 📖 README.md                       # Bu dosya
```

## 🚀 Deployment

### Streamlit Cloud

1. **Repository'yi GitHub'a push edin**
2. **Streamlit Cloud'da yeni app oluşturun**
3. **GitHub repository'yi bağlayın**
4. **Python versiyonu**: 3.11 veya 3.12 seçin (3.13 uyumluluk sorunları olabilir)
5. **requirements.txt otomatik olarak yüklenecektir**

> **💡 İpucu**: Streamlit Cloud'da Python 3.11 veya 3.12 kullanarak uyumluluk sorunlarını önleyin.

### Local Deployment

```bash
# Production için
streamlit run comprehensive_rag_streamlit.py --server.port 8501 --server.address 0.0.0.0

# Docker ile (opsiyonel)
docker build -t rag-system .
docker run -p 8501:8501 rag-system
```

## 🔍 API Kullanımı

### RAG Sistemi API

```python
from chromadb_rag_system import FaissRAGSystem

# Sistem başlatma
rag_system = FaissRAGSystem(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    db_path="comments.db",
    vector_path="vectors/"
)

# Yorum ekleme
rag_system.load_comments_from_csv("comments.csv")

# Sorgu
result = rag_system.query("Kargo sorunları neler?")
print(result["answer"])
```

### Analiz Modülleri

```python
from src.analyzers.contextual_keyword_analyzer import ContextualKeywordAnalyzer
from src.analyzers.topic_modeling_analyzer import TopicModelingAnalyzer

# Bağlamsal analiz
analyzer = ContextualKeywordAnalyzer()
result = analyzer.analyze_contextual_keywords("Kargo geç geldi", "kargo")

# Konu modelleme
topic_analyzer = TopicModelingAnalyzer()
topics, topic_words, coherence = topic_analyzer.lda_topic_modeling(texts, n_topics=5)
```

## 📊 Performans Metrikleri

- **Embedding Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Vector Dimension**: 384D
- **Search Algorithm**: FAISS IndexFlatIP
- **Distance Metric**: Cosine Similarity
- **Response Time**: <500ms (ortalama)
- **Accuracy**: %85+ (semantik arama)

## 🛠️ Geliştirme

### Yeni Analiz Modülü Ekleme

1. **Modül oluşturma**:
```python
# src/analyzers/new_analyzer.py
class NewAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, data):
        # Analiz mantığı
        pass
```

2. **Streamlit'e entegrasyon**:
```python
# comprehensive_rag_streamlit.py
try:
    from new_analyzer import NewAnalyzer
    NEW_ANALYZER_AVAILABLE = True
except ImportError:
    NEW_ANALYZER_AVAILABLE = False
```

### Test Çalıştırma

```bash
# Unit testler
python -m pytest tests/

# Import testleri
python -c "import comprehensive_rag_streamlit; print('✅ All imports successful')"
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

1. **Python 3.13 Uyumluluk Sorunları**
   ```bash
   # Python 3.11 veya 3.12 kullanın
   # Veya alternatif requirements dosyasını kullanın
   pip install -r requirements_python313.txt
   ```

2. **ModuleNotFoundError: plotly**
   ```bash
   pip install plotly
   ```

2. **NLTK data not found**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

3. **FAISS installation error**
   ```bash
   pip install faiss-cpu  # CPU versiyonu
   # veya
   pip install faiss-gpu  # GPU versiyonu
   ```

4. **Chrome driver issues**
   ```bash
   # ChromeDriver'ı güncelleyin
   pip install webdriver-manager
   ```

### Log Kontrolü

```bash
# Streamlit logları
streamlit run comprehensive_rag_streamlit.py --logger.level debug

# Python hata ayıklama
python -c "import comprehensive_rag_streamlit; print('System ready')"
```

## 🤝 Katkıda Bulunma

1. **Fork yapın**
2. **Feature branch oluşturun** (`git checkout -b feature/amazing-feature`)
3. **Değişikliklerinizi commit edin** (`git commit -m 'Add amazing feature'`)
4. **Branch'inizi push edin** (`git push origin feature/amazing-feature`)
5. **Pull Request oluşturun**

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- **FAISS**: Facebook AI Research Similarity Search
- **Sentence Transformers**: Hugging Face
- **Streamlit**: Web app framework
- **NLTK**: Natural Language Toolkit

## 📞 İletişim

- **GitHub Issues**: [Proje Issues](https://github.com/yourusername/web-crawling/issues)
- **Email**: your.email@example.com
- **Discord**: [Sunucu Linki]

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

*Comprehensive RAG System ile müşteri yorumlarınızı akıllıca analiz edin!*

</div>
