import streamlit as st
import json
from datetime import datetime
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from langchain_chromadb_rag import LangChainChromaRAG
except ImportError:
    st.error("❌ LangChain RAG modülü yüklenemedi. requirements_langchain_rag.txt kurulumunu kontrol edin.")
    st.stop()

# Streamlit page config
st.set_page_config(
    page_title="🤖 Trendyol RAG Chat",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35 0%, #FF8E35 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #FF6B35;
        background-color: #f8f9fa;
    }
    .source-box {
        background-color: #e9ecef;
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Trendyol Yorum Analizi RAG Chat</h1>
    <p>LangChain + ChromaDB ile Akıllı Yorum Analizi</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Sistem Kontrolü
with st.sidebar:
    st.header("🔧 Sistem Kontrolü")
    
    # RAG sistemi durumu
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
        st.session_state.system_ready = False
    
    # Sistem kurulumu
    st.subheader("📊 Veri Yükleme")
    
    # CSV dosyası seçimi
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    selected_csv = st.selectbox(
        "CSV Dosyası Seç:",
        csv_files,
        index=csv_files.index('trendyol_comments.csv') if 'trendyol_comments.csv' in csv_files else 0
    )
    
    # LLM seçimi
    st.subheader("🤖 LLM Seçimi")
    llm_type = st.radio(
        "LLM Tipi:",
        ["HuggingFace (Ücretsiz)", "OpenAI (API Key Gerekli)", "Ollama (Local)"],
        help="HuggingFace ücretsiz ama yavaş. OpenAI hızlı ama ücretli. Ollama local ama kurulum gerekli."
    )
    
    # API Key (OpenAI için)
    api_key = None
    if llm_type == "OpenAI (API Key Gerekli)":
        api_key = st.text_input("OpenAI API Key:", type="password")
    
    # Sistem başlatma
    if st.button("🚀 RAG Sistemini Başlat", type="primary"):
        with st.spinner("RAG sistemi kuruluyor..."):
            try:
                # RAG sistemi oluştur
                use_openai = llm_type == "OpenAI (API Key Gerekli)"
                
                st.session_state.rag_system = LangChainChromaRAG(
                    persist_directory="./streamlit_chroma_db",
                    use_openai=use_openai,
                    openai_api_key=api_key
                )
                
                # CSV yükle
                doc_count = st.session_state.rag_system.load_comments_to_vectorstore(selected_csv)
                
                # Harici bilgi ekle
                external_knowledge = {
                    "cozum_onerileri": [
                        "Kargo sorunları için alternatif teslimat seçenekleri sunun",
                        "Kalite kontrolü için üçüncü parti test laboratuvarları kullanın",
                        "Beden uyumsuzluğu için AR (Artırılmış Gerçeklik) deneme özelliği ekleyin",
                        "Müşteri hizmetleri yanıt süresini 2 saate düşürün"
                    ],
                    "kalite_standartlari": {
                        "tekstil": "ISO 3758 etiketleme standardı",
                        "elektronik": "CE ve ROHS sertifikaları zorunlu",
                        "kozmetik": "FDA ve EMA onayları gerekli"
                    },
                    "kargo_politikalari": {
                        "standart_teslimat": "3-5 iş günü",
                        "hızlı_teslimat": "1-2 iş günü",
                        "ücretsiz_kargo_limiti": "150 TL"
                    }
                }
                
                st.session_state.rag_system.add_external_knowledge(external_knowledge)
                
                # LLM chain kur
                if llm_type == "HuggingFace (Ücretsiz)":
                    # Sadece retrieval, LLM olmadan
                    st.session_state.system_ready = True
                    st.session_state.llm_ready = False
                elif llm_type == "OpenAI (API Key Gerekli)":
                    st.session_state.rag_system.setup_retrieval_chain("openai", "gpt-3.5-turbo")
                    st.session_state.system_ready = True
                    st.session_state.llm_ready = True
                elif llm_type == "Ollama (Local)":
                    try:
                        st.session_state.rag_system.setup_retrieval_chain("ollama", "llama2:7b")
                        st.session_state.system_ready = True
                        st.session_state.llm_ready = True
                    except Exception as e:
                        st.warning(f"Ollama bağlantısı başarısız: {e}")
                        st.session_state.system_ready = True
                        st.session_state.llm_ready = False
                
                st.success(f"✅ Sistem hazır! {doc_count} doküman yüklendi.")
                
            except Exception as e:
                st.error(f"❌ Sistem başlatma hatası: {str(e)}")
                st.session_state.system_ready = False
    
    # Sistem durumu
    if st.session_state.system_ready:
        st.success("✅ RAG Sistemi Aktif")
        if st.session_state.get('llm_ready', False):
            st.success("✅ LLM Hazır")
        else:
            st.warning("⚠️ Sadece Retrieval Modu")
    else:
        st.error("❌ Sistem Pasif")
    
    # Sistem sıfırlama
    if st.button("🗑️ Sistemi Sıfırla"):
        if st.session_state.rag_system:
            st.session_state.rag_system.reset_vectorstore()
        st.session_state.rag_system = None
        st.session_state.system_ready = False
        st.rerun()

# Ana içerik alanı
if st.session_state.system_ready:
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analiz", "🔍 Arama"])
    
    with tab1:
        st.header("💬 RAG Chat")
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat input
        user_question = st.text_input(
            "Sorunuzu yazın:",
            placeholder="Örn: Kargo sorunları hakkında ne tür şikayetler var?",
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            ask_button = st.button("🚀 Sor", type="primary")
        
        with col2:
            clear_chat = st.button("🗑️ Temizle")
        
        if clear_chat:
            st.session_state.chat_history = []
            st.rerun()
        
        if ask_button and user_question:
            with st.spinner("🤔 Düşünüyor..."):
                try:
                    if st.session_state.get('llm_ready', False):
                        # Tam RAG yanıtı
                        result = st.session_state.rag_system.query(user_question)
                        
                        # Chat history'e ekle
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "question": user_question,
                            "answer": result["answer"],
                            "sources": result.get("sources", [])
                        })
                    else:
                        # Sadece retrieval
                        similar_docs = st.session_state.rag_system.get_similar_comments(user_question)
                        
                        answer = "**Benzer Yorumlar Bulundu:**\n\n"
                        for i, doc in enumerate(similar_docs[:3], 1):
                            answer += f"**{i}.** {doc['content'][:200]}...\n\n"
                        
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "question": user_question,
                            "answer": answer,
                            "sources": similar_docs
                        })
                    
                except Exception as e:
                    st.error(f"❌ Sorgu hatası: {str(e)}")
            
            st.rerun()
        
        # Chat history göster
        for chat in reversed(st.session_state.chat_history[-5:]):  # Son 5 mesaj
            with st.container():
                st.markdown(f"""
                <div class="chat-message">
                    <strong>🕐 {chat['timestamp']} - Soru:</strong><br>
                    {chat['question']}<br><br>
                    <strong>🤖 Yanıt:</strong><br>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                # Kaynakları göster
                if chat.get('sources'):
                    with st.expander(f"📚 Kaynaklar ({len(chat['sources'])})"):
                        for i, source in enumerate(chat['sources'][:3], 1):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Kaynak {i}:</strong><br>
                                {source.get('content', 'N/A')[:150]}...<br>
                                <em>Metadata: {source.get('metadata', {})}</em>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab2:
        st.header("📊 Trend Analizi")
        
        if st.button("🔄 Analizi Yenile"):
            with st.spinner("Analiz yapılıyor..."):
                trends = st.session_state.rag_system.analyze_trends()
                
                # Metrikler
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Toplam Yorum",
                        trends["total_comments"]
                    )
                
                with col2:
                    st.metric(
                        "Ortalama Öncelik",
                        f"{trends['priority_stats']['average_priority']}/100"
                    )
                
                with col3:
                    st.metric(
                        "Yüksek Öncelikli",
                        trends['priority_stats']['high_priority_count']
                    )
                
                with col4:
                    st.metric(
                        "Kritik Oran",
                        f"%{trends['priority_stats']['high_priority_percentage']}"
                    )
                
                # Kategori dağılımı
                st.subheader("📈 Kategori Dağılımı")
                category_data = trends["category_distribution"]
                if category_data:
                    st.bar_chart(category_data)
                
                # Acil kategoriler
                st.subheader("🚨 Acil Kategoriler")
                urgent_data = trends["urgent_category_distribution"]
                if urgent_data:
                    st.bar_chart(urgent_data)
                
                # JSON gösterimi
                with st.expander("🔍 Detaylı Analiz (JSON)"):
                    st.json(trends)
    
    with tab3:
        st.header("🔍 Benzer Yorum Arama")
        
        search_query = st.text_input(
            "Arama terimi:",
            placeholder="Örn: kargo gecikme"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            search_count = st.slider("Sonuç sayısı:", 1, 10, 5)
        with col2:
            min_priority = st.slider("Minimum öncelik skoru:", 0, 100, 0)
        
        if st.button("🔍 Ara") and search_query:
            with st.spinner("Aranıyor..."):
                filter_by = {"priority_score": {"$gte": min_priority}} if min_priority > 0 else None
                
                similar_comments = st.session_state.rag_system.get_similar_comments(
                    search_query,
                    k=search_count,
                    filter_by=filter_by
                )
                
                st.subheader(f"📋 {len(similar_comments)} Benzer Yorum")
                
                for i, comment in enumerate(similar_comments, 1):
                    with st.expander(f"Yorum {i} - Öncelik: {comment['metadata'].get('priority_score', 'N/A')}"):
                        st.markdown(comment['content'])
                        st.json(comment['metadata'])

else:
    # Sistem kurulmamışsa
    st.warning("⚠️ Lütfen önce RAG sistemini başlatın.")
    
    st.markdown("""
    ## 🚀 Başlangıç Rehberi
    
    1. **📊 Veri Yükleme**: Sol panelden CSV dosyanızı seçin
    2. **🤖 LLM Seçimi**: Kullanmak istediğiniz AI modelini seçin
    3. **🚀 Sistem Başlatma**: "RAG Sistemini Başlat" butonuna tıklayın
    4. **💬 Chat**: Yorumlar hakkında soru sorun
    
    ### 🤖 Model Seçenekleri:
    
    - **HuggingFace**: Ücretsiz, yavaş, sadece retrieval
    - **OpenAI**: Hızlı, ücretli, tam RAG deneyimi
    - **Ollama**: Local, ücretsiz, kurulum gerekli
    
    ### 💡 Örnek Sorular:
    
    - "Kargo sorunları hakkında ne tür şikayetler var?"
    - "En yüksek öncelikli problemler neler?"
    - "Kalite konusunda hangi ürünlerde sorun yaşanıyor?"
    - "Müşteri memnuniyetini artırmak için ne önerirsin?"
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🛍️ <strong>Trendyol RAG Chat</strong> - LangChain + ChromaDB ile güçlendirilmiştir<br>
    💡 <em>Büyük veri setleri için optimize edilmiş akıllı yorum analizi</em>
</div>
""", unsafe_allow_html=True) 