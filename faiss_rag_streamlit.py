#!/usr/bin/env python3
"""
🚀 FAISS RAG Streamlit Arayüzü
Modern vector search ile semantic similarity
"""

import streamlit as st
import pandas as pd
import json
import numpy as np
from datetime import datetime
from chromadb_rag_system import FaissRAGSystem, setup_demo_knowledge

# Streamlit page config
st.set_page_config(
    page_title="🚀 FAISS RAG Chat",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35 0%, #FF8E35 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #FF6B35;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
    .tech-badge {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    .similarity-score {
        background: #e1f5fe;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-weight: bold;
        color: #0277bd;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 FAISS Vector RAG Chat</h1>
    <p>Facebook AI Similarity Search • Sentence Transformers • Semantic Search</p>
    <div>
        <span class="tech-badge">FAISS</span>
        <span class="tech-badge">384D Embeddings</span>
        <span class="tech-badge">Cosine Similarity</span>
        <span class="tech-badge">Türkçe NLP</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'faiss_rag_system' not in st.session_state:
    st.session_state.faiss_rag_system = None
    st.session_state.system_ready = False
    st.session_state.chat_history = []
    st.session_state.model_loading = False

# Sidebar
with st.sidebar:
    st.header("🔧 FAISS Sistem Kontrolü")
    
    # Model seçimi
    st.subheader("🧠 Embedding Model")
    
    model_options = {
        "Türkçe Optimized (Önerilen)": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "Çok Dilli Genel": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "Hızlı & Küçük": "sentence-transformers/all-MiniLM-L6-v2"
    }
    
    selected_model_name = st.selectbox(
        "Model Seçin:",
        list(model_options.keys()),
        help="Türkçe için optimize edilmiş model önerilir"
    )
    selected_model = model_options[selected_model_name]
    
    # Sistem kurulumu
    st.subheader("📊 Sistem Başlatma")
    
    if st.button("🚀 FAISS RAG Sistemini Başlat", type="primary"):
        with st.spinner("🧠 Embedding modeli yükleniyor..."):
            st.session_state.model_loading = True
            try:
                # FAISS RAG sistemi oluştur
                st.session_state.faiss_rag_system = FaissRAGSystem(
                    model_name=selected_model,
                    db_path="streamlit_faiss_rag.db",
                    vector_path="./streamlit_faiss_vectors"
                )
                
                # CSV yükle
                doc_count = st.session_state.faiss_rag_system.load_comments_from_csv("trendyol_comments.csv")
                
                if doc_count > 0 or st.session_state.faiss_rag_system.get_stats()['total_comments'] > 0:
                    # Demo bilgi tabanını kur (sadece yeni kurulumda)
                    if doc_count > 0:
                        setup_demo_knowledge(st.session_state.faiss_rag_system)
                    
                    st.session_state.system_ready = True
                    st.session_state.model_loading = False
                    st.success(f"✅ Sistem hazır! Model: {selected_model_name}")
                    st.rerun()
                else:
                    st.error("❌ CSV dosyası bulunamadı!")
                    st.info("💡 Önce `trendyol_selenium_scraper.py` çalıştırın")
                    st.session_state.model_loading = False
                
            except Exception as e:
                st.error(f"❌ Sistem kurulum hatası: {str(e)}")
                st.session_state.system_ready = False
                st.session_state.model_loading = False
    
    # Loading durumu
    if st.session_state.model_loading:
        st.info("⏳ Model yükleniyor, lütfen bekleyin...")
    
    # Sistem durumu
    if st.session_state.system_ready:
        st.success("✅ FAISS RAG Sistemi Aktif")
        
        # İstatistikler
        stats = st.session_state.faiss_rag_system.get_stats()
        
        st.subheader("📈 Sistem Metrikleri")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Vector Yorumlar", stats['vector_comments'])
            st.metric("Bilgi Tabanı", stats['total_knowledge_entries'])
        
        with col2:
            st.metric("Embedding Boyut", f"{stats['embedding_dimension']}D")
            st.metric("Ortalama Öncelik", f"{stats['average_priority']:.1f}/100")
        
        # Model bilgileri
        st.subheader("🧠 Model Bilgileri")
        st.code(stats['embedding_model'])
        
        # Kategori dağılımı
        if stats['category_distribution']:
            st.subheader("📊 Kategori Dağılımı")
            category_data = stats['category_distribution']
            st.bar_chart(category_data)
    
    else:
        st.error("❌ Sistem Pasif")
    
    # Advanced Settings
    with st.expander("⚙️ Gelişmiş Ayarlar"):
        similarity_threshold = st.slider(
            "Benzerlik Eşiği:",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            help="Düşük değer = daha fazla sonuç, Yüksek değer = daha kaliteli sonuç"
        )
        
        max_results = st.slider("Maksimum Sonuç:", 1, 10, 5)
    
    # Sistem sıfırlama
    if st.button("🗑️ Vektörleri Sıfırla"):
        if st.session_state.faiss_rag_system:
            st.session_state.faiss_rag_system.reset_vectors()
        st.session_state.faiss_rag_system = None
        st.session_state.system_ready = False
        st.session_state.chat_history = []
        st.rerun()

# Ana içerik
if st.session_state.system_ready:
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Semantic Chat", "🔍 Vector Search", "📊 Analytics", "🧠 Tech Details"])
    
    with tab1:
        st.header("💬 Semantic RAG Chat")
        st.caption("Natural language queries with vector similarity search")
        
        # Chat input
        user_question = st.text_input(
            "🔍 Sorunuzu yazın:",
            placeholder="Örn: Kargo sorunları hakkında müşteriler ne diyor?",
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            ask_button = st.button("🚀 Semantic Search", type="primary")
        with col2:
            if st.button("🗑️ Chat Geçmişi"):
                st.session_state.chat_history = []
                st.rerun()
        
        if ask_button and user_question:
            with st.spinner("🧠 Vector similarity hesaplanıyor..."):
                try:
                    result = st.session_state.faiss_rag_system.query(user_question)
                    
                    # Chat history'e ekle
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "question": user_question,
                        "answer": result["answer"],
                        "similar_comments": result.get("similar_comments", []),
                        "knowledge_results": result.get("knowledge_results", []),
                        "model": result.get("embedding_model", "")
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
                    <em>{chat['question']}</em><br><br>
                    <strong>🤖 AI Yanıt:</strong><br>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                # Detaylı sonuçları göster
                if chat.get('similar_comments') or chat.get('knowledge_results'):
                    with st.expander(f"🔬 Vector Search Details - Semantic: {len(chat.get('similar_comments', []))}, Knowledge: {len(chat.get('knowledge_results', []))}"):
                        
                        if chat.get('similar_comments'):
                            st.subheader("📝 Semantically Similar Comments")
                            for i, comment in enumerate(chat['similar_comments'][:3], 1):
                                similarity = comment['similarity']
                                color = "green" if similarity > 0.7 else "orange" if similarity > 0.5 else "red"
                                
                                st.markdown(f"""
                                **{i}.** {comment['comment'][:120]}...
                                
                                📊 **Metrics:** <span class="similarity-score">Similarity: {similarity:.3f}</span> | 
                                Priority: {comment['priority_score']:.0f}/100 | Category: {comment['category']}
                                """, unsafe_allow_html=True)
                        
                        if chat.get('knowledge_results'):
                            st.subheader("💡 Knowledge Base Matches")
                            for i, kb in enumerate(chat['knowledge_results'], 1):
                                similarity = kb['similarity']
                                st.markdown(f"""
                                **{i}. {kb['category'].title()}** <span class="similarity-score">{similarity:.3f}</span>
                                
                                **Problem:** {kb['problem']}
                                
                                **Solution:** {kb['solution']}
                                """, unsafe_allow_html=True)
    
    with tab2:
        st.header("🔍 Advanced Vector Search")
        st.caption("Direct FAISS similarity search with custom parameters")
        
        search_query = st.text_input(
            "Vector search query:",
            placeholder="Örn: kalite sorunu, beden uyumsuz"
        )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_count = st.slider("Results:", 1, 15, 5)
        with col2:
            search_threshold = st.slider("Threshold:", 0.0, 1.0, 0.3, 0.05)
        with col3:
            search_type = st.selectbox("Type:", ["Comments", "Knowledge", "Both"])
        with col4:
            sentiment_filter = st.selectbox("Sentiment:", ["All", "Negative Only", "Positive Only"])
        
        if st.button("🔍 Vector Search") and search_query:
            with st.spinner("🧮 FAISS searching..."):
                
                if search_type in ["Comments", "Both"]:
                    st.subheader("📝 Similar Comment Vectors")
                    
                    # Sentiment filter mapping
                    sentiment_map = {
                        "All": None,
                        "Negative Only": "negative", 
                        "Positive Only": "positive"
                    }
                    
                    similar_comments = st.session_state.faiss_rag_system.search_similar_comments(
                        search_query, 
                        limit=search_count,
                        similarity_threshold=search_threshold,
                        sentiment_filter=sentiment_map[sentiment_filter]
                    )
                    
                    if similar_comments:
                        for i, comment in enumerate(similar_comments, 1):
                            similarity = comment['similarity']
                            
                            # Sentiment detection for display
                            comment_text = comment['comment'].lower()
                            negative_keywords = ['sorun', 'problem', 'kötü', 'berbat', 'bozuk', 'defolu', 
                                               'şikayet', 'memnun değil', 'kalitesiz', 'geç', 'yavaş', 'hasarlı', 'kırık',
                                               'iade', 'beğenmedim', 'tavsiye etmem', 'pişman', 'hayal kırıklığı']
                            positive_keywords = ['beğendik', 'beğendim', 'mükemmel', 'harika', 'süper', 'tavsiye ederim', 
                                               'memnun', 'kaliteli', 'güzel', 'vazgeçilmez', 'favorim', 'stok']
                            
                            has_negative = any(kw in comment_text for kw in negative_keywords)
                            has_positive = any(kw in comment_text for kw in positive_keywords)
                            
                            if has_negative and not has_positive:
                                detected_sentiment = "🔴 Negative"
                            elif has_positive and not has_negative:
                                detected_sentiment = "🟢 Positive"
                            else:
                                detected_sentiment = "⚪ Mixed/Neutral"
                            
                            with st.expander(f"Vector {i} - {detected_sentiment} - Similarity: {similarity:.4f}"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Comment:** {comment['comment']}")
                                    st.caption(f"User: {comment['user']} | Date: {comment['date']}")
                                
                                with col2:
                                    st.metric("Similarity", f"{similarity:.4f}")
                                    st.metric("Priority", f"{comment['priority_score']:.0f}/100")
                                    st.text(f"Category: {comment['category']}")
                                    st.text(f"Sentiment: {detected_sentiment}")
                    else:
                        if sentiment_filter == "Negative Only":
                            st.warning("⚠️ Bu arama terimi için olumsuz yorum bulunamadı.")
                            st.info("💡 Farklı anahtar kelimeler deneyin veya eşik değerini düşürün.")
                        elif sentiment_filter == "Positive Only":
                            st.warning("⚠️ Bu arama terimi için olumlu yorum bulunamadı.")
                            st.info("💡 Farklı anahtar kelimeler deneyin veya eşik değerini düşürün.")
                        else:
                            st.info("No vectors found above threshold.")
                
                if search_type in ["Knowledge", "Both"]:
                    st.subheader("💡 Knowledge Base Vectors")
                    kb_results = st.session_state.faiss_rag_system.search_knowledge_base(
                        search_query,
                        limit=search_count,
                        similarity_threshold=search_threshold
                    )
                    
                    if kb_results:
                        for i, kb in enumerate(kb_results, 1):
                            similarity = kb['similarity']
                            
                            with st.expander(f"Knowledge {i} - {kb['category'].title()} - {similarity:.4f}"):
                                st.write(f"**Problem:** {kb['problem']}")
                                st.write(f"**Solution:** {kb['solution']}")
                                st.metric("Vector Similarity", f"{similarity:.4f}")
                                if kb['keywords']:
                                    st.write(f"**Keywords:** {', '.join(kb['keywords'])}")
                    else:
                        st.info("No knowledge vectors found above threshold.")
    
    with tab3:
        st.header("📊 Vector Analytics")
        
        if st.button("🔄 Refresh Analytics"):
            stats = st.session_state.faiss_rag_system.get_stats()
            
            # Genel metrikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Vectors", stats['vector_comments'])
            with col2:
                st.metric("Knowledge Vectors", stats['vector_knowledge'])
            with col3:
                st.metric("Embedding Dimension", f"{stats['embedding_dimension']}D")
            with col4:
                st.metric("Avg Priority", f"{stats['average_priority']:.1f}")
            
            # Vector space analizi
            st.subheader("🔬 Vector Space Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if stats['category_distribution']:
                    st.subheader("📈 Category Distribution")
                    category_df = pd.DataFrame(
                        list(stats['category_distribution'].items()),
                        columns=['Category', 'Count']
                    )
                    category_df['Percentage'] = (category_df['Count'] / category_df['Count'].sum() * 100).round(1)
                    
                    st.bar_chart(category_df.set_index('Category')['Count'])
                    st.dataframe(category_df, hide_index=True)
            
            with col2:
                st.subheader("🧠 Model Information")
                model_info = {
                    "Model": stats['embedding_model'].split('/')[-1],
                    "Dimension": f"{stats['embedding_dimension']}",
                    "Distance Metric": "Cosine Similarity (Inner Product)",
                    "Index Type": "FAISS IndexFlatIP",
                    "Memory Usage": "~384 bytes per vector",
                    "Language Support": "Multilingual (Turkish optimized)"
                }
                
                for key, value in model_info.items():
                    st.metric(key, value)
    
    with tab4:
        st.header("🧠 Technical Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔬 FAISS Configuration")
            st.code("""
# FAISS Index Configuration
Index Type: IndexFlatIP (Inner Product)
Distance: Cosine Similarity
Dimension: 384
Storage: Persistent to disk

# Search Parameters  
Similarity Threshold: 0.3
Max Results: 5-15
Batch Processing: 32 vectors/batch
            """)
            
            st.subheader("📊 Vector Statistics")
            if st.session_state.system_ready:
                stats = st.session_state.faiss_rag_system.get_stats()
                st.json({
                    "comment_vectors": stats['vector_comments'],
                    "knowledge_vectors": stats['vector_knowledge'],
                    "embedding_model": stats['embedding_model'],
                    "dimension": stats['embedding_dimension'],
                    "total_db_records": stats['total_comments']
                })
        
        with col2:
            st.subheader("🧬 Embedding Model Details")
            if st.session_state.system_ready:
                # Model name'i doğru şekilde al
                model_name = st.session_state.faiss_rag_system.model_name
                st.write(f"**Model:** {model_name}")
                st.write(f"**Architecture:** Sentence-BERT")
                st.write(f"**Max Length:** 512 tokens")
                st.write(f"**Languages:** Turkish, English, 50+ others")
                
            st.subheader("⚡ Performance Metrics")
            st.code("""
Vector Search: ~1ms per query
Embedding Generation: ~30ms per text
Index Build: ~2s per 1000 vectors
Memory Usage: 384 bytes × vector_count
Disk Storage: Persistent with pickle
            """)

else:
    # Sistem kurulmamışsa
    st.warning("⚠️ FAISS RAG sistemini başlatın.")
    
    st.markdown("""
    ## 🚀 FAISS Vector RAG System
    
    ### 🔬 Technical Features:
    
    - **🧠 Sentence Transformers**: 384-dimensional multilingual embeddings
    - **⚡ FAISS**: Facebook AI's optimized similarity search
    - **🎯 Semantic Search**: Understanding meaning, not just keywords
    - **📊 Cosine Similarity**: Advanced vector distance metrics
    - **💾 Persistent Storage**: Vectors saved to disk for fast reload
    
    ### 💡 Example Queries:
    
    - "Kargo gecikmeleri hakkında müşteri şikayetleri neler?"
    - "Ürün kalitesinde en sık karşılaşılan sorunlar hangileri?"
    - "Beden tablosunda yaşanan problemler nasıl çözülebilir?"
    - "Website kullanıcı deneyimi için öneriler"
    
    ### 🎯 Advantages Over Traditional Search:
    
    - **Semantic Understanding**: "teslimat gecikti" → "kargo sorunları"
    - **Context Awareness**: Related concepts automatically matched
    - **Multilingual Support**: Turkish, English, and 50+ languages
    - **Fast Vector Search**: Sub-millisecond query performance
    - **Scalable Storage**: Efficient memory and disk usage
    
    ### 🛠️ Getting Started:
    
    1. **Select Model**: Choose embedding model for your use case
    2. **Load Data**: CSV comments automatically vectorized
    3. **Start Chatting**: Ask natural language questions
    4. **Explore Vectors**: Use advanced search for technical analysis
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🚀 <strong>FAISS Vector RAG</strong> - Powered by Facebook AI Similarity Search<br>
    🧠 <em>Sentence Transformers • 384D Embeddings • Semantic Understanding</em>
</div>
""", unsafe_allow_html=True) 