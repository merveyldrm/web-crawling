import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import CSVLoader, TextLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.llms import OpenAI, Ollama
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# ChromaDB
import chromadb
from chromadb.config import Settings

# Local imports
from advanced_comment_analyzer import AdvancedCommentAnalyzer
from priority_analyzer import PriorityAnalyzer

class LangChainChromaRAG:
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        use_openai: bool = False,
        openai_api_key: str = None,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Gelişmiş RAG sistemi - LangChain + ChromaDB
        
        Args:
            persist_directory: ChromaDB'nin saklanacağı dizin
            use_openai: OpenAI embeddings kullanılsın mı
            openai_api_key: OpenAI API anahtarı
            model_name: Embedding modeli adı
        """
        self.persist_directory = persist_directory
        self.use_openai = use_openai
        
        # Dizin oluştur
        Path(persist_directory).mkdir(exist_ok=True)
        
        # Embeddings seçimi
        if use_openai and openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            self.embeddings = OpenAIEmbeddings()
            print("✅ OpenAI embeddings kullanılacak")
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'}  # GPU varsa 'cuda' yapın
            )
            print(f"✅ HuggingFace embeddings: {model_name}")
        
        # ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Vector store
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Local analyzers
        self.comment_analyzer = AdvancedCommentAnalyzer()
        self.priority_analyzer = PriorityAnalyzer()
        
        # Memory for conversations
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        print("🚀 LangChain + ChromaDB RAG sistemi başlatıldı")
    
    def load_comments_to_vectorstore(
        self,
        csv_file: str = "trendyol_comments.csv",
        collection_name: str = "trendyol_comments"
    ) -> int:
        """
        Yorumları CSV'den yükleyip ChromaDB'ye vektörize ederek kaydet
        
        Returns:
            Yüklenen doküman sayısı
        """
        print(f"📊 Yorumlar yükleniyor: {csv_file}")
        
        # CSV dosyasını oku
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f"📁 {len(df)} yorum bulundu")
        except Exception as e:
            print(f"❌ CSV okuma hatası: {e}")
            return 0
        
        # Documents listesi oluştur
        documents = []
        
        for idx, row in df.iterrows():
            # Yorum analizi yap
            analysis = self.comment_analyzer.analyze_comment(str(row.get('comment', '')))
            priority = self.priority_analyzer.analyze_comment_priority(str(row.get('comment', '')))
            
            # Metadata oluştur
            metadata = {
                'source': 'trendyol_csv',
                'user': str(row.get('user', 'Unknown')),
                'date': str(row.get('date', '')),
                'comment_id': str(idx),
                'sentiment_category': analysis.get('category_analysis', {}).get('highest_category', 'unknown'),
                'sentiment_confidence': analysis.get('category_analysis', {}).get('highest_confidence', 0.0),
                'priority_score': priority.get('priority_score', 0),
                'urgent_category': priority.get('urgent_category', 'none'),
                'chunk_id': f"comment_{idx}"
            }
            
            # Document oluştur
            doc_content = f"""
Kullanıcı: {row.get('user', 'Anonim')}
Tarih: {row.get('date', 'Bilinmiyor')}
Yorum: {row.get('comment', '')}

Analiz Özeti:
- Kategori: {analysis.get('category_analysis', {}).get('highest_category', 'unknown')}
- Güven: {analysis.get('category_analysis', {}).get('highest_confidence', 0.0):.2f}
- Öncelik: {priority.get('priority_score', 0)}/100
- Acil Kategori: {priority.get('urgent_category', 'none')}
            """.strip()
            
            document = Document(
                page_content=doc_content,
                metadata=metadata
            )
            
            documents.append(document)
        
        # Text splitting (opsiyonel, yorumlar genelde kısa olduğu için)
        print("✂️ Metin bölümleniyor...")
        split_docs = self.text_splitter.split_documents(documents)
        print(f"📄 {len(split_docs)} doküman parçası oluşturuldu")
        
        # ChromaDB'ye kaydet
        print("💾 ChromaDB'ye kaydediliyor...")
        self.vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        
        self.vector_store.persist()
        print(f"✅ {len(split_docs)} doküman ChromaDB'ye kaydedildi")
        
        return len(split_docs)
    
    def add_external_knowledge(
        self,
        knowledge_sources: Dict[str, Any],
        collection_name: str = "external_knowledge"
    ):
        """
        Harici bilgi kaynaklarını vector store'a ekle
        
        Args:
            knowledge_sources: Bilgi kaynakları dict'i
        """
        print("🌐 Harici bilgi kaynakları ekleniyor...")
        
        documents = []
        
        for source_name, source_data in knowledge_sources.items():
            if isinstance(source_data, dict):
                content = json.dumps(source_data, ensure_ascii=False, indent=2)
                doc_type = "structured_data"
            elif isinstance(source_data, list):
                content = "\n".join(str(item) for item in source_data)
                doc_type = "list_data"
            else:
                content = str(source_data)
                doc_type = "text_data"
            
            metadata = {
                'source': 'external_knowledge',
                'source_name': source_name,
                'doc_type': doc_type,
                'created_at': datetime.now().isoformat(),
                'chunk_id': f"ext_{source_name}"
            }
            
            document = Document(
                page_content=f"Kaynak: {source_name}\n\nİçerik:\n{content}",
                metadata=metadata
            )
            
            documents.append(document)
        
        # Text splitting
        split_docs = self.text_splitter.split_documents(documents)
        
        # Eğer vector store yoksa oluştur
        if self.vector_store is None:
            self.vector_store = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )
        else:
            # Mevcut vector store'a ekle
            self.vector_store.add_documents(split_docs)
        
        self.vector_store.persist()
        print(f"✅ {len(split_docs)} harici bilgi kaynağı eklendi")
    
    def setup_retrieval_chain(
        self,
        llm_type: str = "openai",  # "openai" or "ollama"
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        k: int = 4  # Retrieve top-k documents
    ):
        """
        Retrieval QA chain'ini kur
        
        Args:
            llm_type: LLM tipi
            model_name: Model adı
            temperature: Yaratıcılık seviyesi
            k: Kaç doküman çekilecek
        """
        print(f"🤖 {llm_type.upper()} LLM chain kuruluyor...")
        
        if self.vector_store is None:
            raise ValueError("❌ Vector store henüz oluşturulmamış! Önce load_comments_to_vectorstore() çalıştırın.")
        
        # LLM seçimi
        if llm_type == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("❌ OPENAI_API_KEY environment variable gerekli!")
            llm = OpenAI(temperature=temperature, model_name=model_name)
        elif llm_type == "ollama":
            llm = Ollama(model=model_name, temperature=temperature)
        else:
            raise ValueError(f"❌ Desteklenmeyen LLM tipi: {llm_type}")
        
        # Retriever kur
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Turkish-specific prompt template
        prompt_template = """
Trendyol ürün yorumları ve ilgili bilgi kaynaklarını kullanarak soruyu yanıtla.

Bağlam Bilgiler:
{context}

Soru: {question}

Yanıt Kuralları:
1. Sadece verilen bağlam bilgilerini kullan
2. Türkçe ve anlaşılır bir dille yanıt ver
3. Spesifik örnekler ve veri noktaları kullan
4. Eğer cevap bağlamda yoksa "Bu sorunun cevabı mevcut verilerde bulunmuyor" de
5. Öncelik skorları ve kategorileri dahil et
6. Pratik çözüm önerileri sun

Yanıt:
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # QA Chain oluştur
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✅ Retrieval QA chain hazır!")
    
    def query(self, question: str, show_sources: bool = True) -> Dict[str, Any]:
        """
        RAG sistemine soru sor
        
        Args:
            question: Soru
            show_sources: Kaynak dokümanları göster
            
        Returns:
            Yanıt ve kaynak bilgileri
        """
        if self.qa_chain is None:
            raise ValueError("❌ QA chain henüz kurulmamış! setup_retrieval_chain() çalıştırın.")
        
        print(f"🔍 Soru işleniyor: {question}")
        
        # Query çalıştır
        result = self.qa_chain({"query": question})
        
        response = {
            "question": question,
            "answer": result["result"],
            "timestamp": datetime.now().isoformat()
        }
        
        if show_sources:
            sources = []
            for doc in result.get("source_documents", []):
                source_info = {
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": getattr(doc, "score", "N/A")
                }
                sources.append(source_info)
            
            response["sources"] = sources
            response["source_count"] = len(sources)
        
        return response
    
    def get_similar_comments(
        self,
        query: str,
        k: int = 5,
        filter_by: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Benzer yorumları bul
        
        Args:
            query: Arama sorgusu
            k: Kaç yorum döndürülecek
            filter_by: Metadata filtresi (örn: {"priority_score": {"$gte": 70}})
        """
        if self.vector_store is None:
            raise ValueError("❌ Vector store henüz oluşturulmamış!")
        
        print(f"🔍 Benzer yorumlar aranıyor: '{query}'")
        
        # Similarity search
        if filter_by:
            results = self.vector_store.similarity_search(
                query, 
                k=k,
                filter=filter_by
            )
        else:
            results = self.vector_store.similarity_search(query, k=k)
        
        similar_comments = []
        for doc in results:
            similar_comments.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, "score", "N/A")
            })
        
        print(f"📊 {len(similar_comments)} benzer yorum bulundu")
        return similar_comments
    
    def analyze_trends(self, category: str = None) -> Dict[str, Any]:
        """
        Trend analizi yap
        
        Args:
            category: Spesifik kategori analizi
        """
        if self.vector_store is None:
            raise ValueError("❌ Vector store henüz oluşturulmamış!")
        
        print(f"📈 Trend analizi: {category or 'Genel'}")
        
        # Tüm dokümanları çek
        all_docs = self.vector_store._collection.get()
        
        # Metadata analizi
        categories = {}
        priority_scores = []
        urgent_categories = {}
        
        for metadata in all_docs.get("metadatas", []):
            # Kategori sayımı
            cat = metadata.get("sentiment_category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            # Öncelik skorları
            priority = metadata.get("priority_score", 0)
            if isinstance(priority, (int, float)):
                priority_scores.append(priority)
            
            # Acil kategoriler
            urgent = metadata.get("urgent_category", "none")
            urgent_categories[urgent] = urgent_categories.get(urgent, 0) + 1
        
        # İstatistikler
        total_comments = len(all_docs.get("metadatas", []))
        avg_priority = sum(priority_scores) / len(priority_scores) if priority_scores else 0
        high_priority_count = len([p for p in priority_scores if p >= 70])
        
        trends = {
            "total_comments": total_comments,
            "category_distribution": categories,
            "urgent_category_distribution": urgent_categories,
            "priority_stats": {
                "average_priority": round(avg_priority, 2),
                "high_priority_count": high_priority_count,
                "high_priority_percentage": round((high_priority_count / total_comments) * 100, 2) if total_comments > 0 else 0
            },
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return trends
    
    def reset_vectorstore(self):
        """Vector store'u sıfırla"""
        import shutil
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            print("🗑️ Vector store sıfırlandı")
        
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None


def main():
    """Demo usage"""
    print("🚀 LangChain + ChromaDB RAG Demo")
    
    # RAG sistemi oluştur
    rag = LangChainChromaRAG(
        persist_directory="./chroma_trendyol_rag",
        use_openai=False,  # HuggingFace kullan (ücretsiz)
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # Örnek harici bilgi kaynakları
    external_knowledge = {
        "kargo_cozumleri": [
            "Kargo gecikmelerine karşı alternatif teslimat seçenekleri sunun",
            "Express kargo ile 1 gün teslimat garantisi verin",
            "Kargo takip SMS/email sistemi kurun"
        ],
        "kalite_standartlari": {
            "tekstil": "Kumaş kalitesi minimum %80 pamuk olmalı",
            "elektronik": "CE sertifikası zorunlu",
            "kozmetik": "Dermatolojik test raporu gerekli"
        },
        "musteri_hizmetleri": {
            "yanit_suresi": "4 saat içinde",
            "cozum_orani": "%95",
            "diller": ["Türkçe", "İngilizce"]
        }
    }
    
    # Yorumları yükle
    rag.load_comments_to_vectorstore("trendyol_comments.csv")
    
    # Harici bilgileri ekle  
    rag.add_external_knowledge(external_knowledge)
    
    # LLM chain kur (Ollama kullanarak)
    try:
        rag.setup_retrieval_chain(
            llm_type="ollama",  # Ücretsiz local LLM
            model_name="llama2:7b",  # veya "mistral"
            temperature=0.1
        )
        
        # Örnek sorgular
        questions = [
            "Kargo sorunları hakkında ne tür şikayetler var?",
            "En yüksek öncelikli problemler neler?",
            "Kalite konusunda hangi ürünlerde sorun yaşanıyor?",
            "Müşteri memnuniyetini artırmak için ne önerirsin?"
        ]
        
        for question in questions:
            print(f"\n{'='*50}")
            print(f"Soru: {question}")
            print('='*50)
            
            result = rag.query(question)
            print(f"Yanıt: {result['answer']}")
            print(f"Kaynak sayısı: {result.get('source_count', 0)}")
            
    except Exception as e:
        print(f"⚠️ LLM setup hatası: {e}")
        print("💡 Ollama kurulumu: https://ollama.ai/download")
        print("💡 Model indirme: ollama pull llama2:7b")
    
    # Trend analizi
    print(f"\n{'='*50}")
    print("📈 TREND ANALİZİ")
    print('='*50)
    
    trends = rag.analyze_trends()
    print(json.dumps(trends, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 