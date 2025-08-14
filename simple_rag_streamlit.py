#!/usr/bin/env python3
"""
🚀 Basit RAG Streamlit Arayüzü
Python 3.13 uyumlu, minimal dependency
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from simple_rag_demo import SimpleRAGSystem, setup_demo_knowledge

# Streamlit page config
st.set_page_config(
    page_title="🛍️ Trendyol RAG Chat",
    page_icon="🤖",
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
    .metric-box {
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
    <h1>🛍️ Trendyol Yorum Analizi RAG Chat</h1>
    <p>Python 3.13 Uyumlu • Minimal Dependency • TF-IDF Tabanlı</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
    st.session_state.system_ready = False
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("🔧 Sistem Kontrolü")
    
    # Sistem kurulumu
    st.subheader("📊 Veri Yükleme")
    
    if st.button("🚀 RAG Sistemini Başlat", type="primary"):
        with st.spinner("RAG sistemi kuruluyor..."):
            try:
                # RAG sistemi oluştur
                st.session_state.rag_system = SimpleRAGSystem("streamlit_rag.db")
                
                # CSV yükle
                doc_count = st.session_state.rag_system.load_comments_from_csv("trendyol_comments.csv")
                
                if doc_count > 0:
                    # Demo bilgi tabanını kur
                    setup_demo_knowledge(st.session_state.rag_system)
                    
                    st.session_state.system_ready = True
                    st.success(f"✅ Sistem hazır! {doc_count} yorum yüklendi.")
                else:
                    st.error("❌ Yorum dosyası bulunamadı!")
                    st.info("💡 Önce `trendyol_selenium_scraper.py` çalıştırın")
                
            except Exception as e:
                st.error(f"❌ Sistem kurulum hatası: {str(e)}")
                st.session_state.system_ready = False
    
    # Sistem durumu
    if st.session_state.system_ready:
        st.success("✅ RAG Sistemi Aktif")
        
        # İstatistikler
        stats = st.session_state.rag_system.get_stats()
        
        st.subheader("📈 Sistem İstatistikleri")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Toplam Yorum", stats['total_comments'])
            st.metric("Bilgi Tabanı", stats['total_knowledge_entries'])
        
        with col2:
            st.metric("Ortalama Öncelik", f"{stats['average_priority']}/100")
            st.metric("Gelişmiş Analiz", "✅" if stats['has_advanced_analyzers'] else "❌")
        
        # Kategori dağılımı
        if stats['category_distribution']:
            st.subheader("📊 Kategori Dağılımı")
            category_data = stats['category_distribution']
            st.bar_chart(category_data)
    
    else:
        st.error("❌ Sistem Pasif")
    
    # Sistem sıfırlama
    if st.button("🗑️ Sistemi Sıfırla"):
        st.session_state.rag_system = None
        st.session_state.system_ready = False
        st.session_state.chat_history = []
        st.rerun()

# Ana içerik
if st.session_state.system_ready:
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Arama", "📊 Analiz"])
    
    with tab1:
        st.header("💬 RAG Chat")
        
        # Chat input
        user_question = st.text_input(
            "Sorunuzu yazın:",
            placeholder="Örn: Kargo sorunları hakkında ne tür şikayetler var?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            ask_button = st.button("🚀 Sor", type="primary")
        with col2:
            if st.button("🗑️ Chat'i Temizle"):
                st.session_state.chat_history = []
                st.rerun()
        
        if ask_button and user_question:
            with st.spinner("🤔 Analiz ediliyor..."):
                try:
                    result = st.session_state.rag_system.query(user_question)
                    
                    # Chat history'e ekle
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "question": user_question,
                        "answer": result["answer"],
                        "similar_comments": result.get("similar_comments", []),
                        "knowledge_results": result.get("knowledge_results", [])
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
                
                # Detayları göster
                if chat.get('similar_comments') or chat.get('knowledge_results'):
                    with st.expander(f"📊 Detaylar - Benzer: {len(chat.get('similar_comments', []))}, Bilgi: {len(chat.get('knowledge_results', []))}"):
                        
                        if chat.get('similar_comments'):
                            st.subheader("📝 Benzer Yorumlar")
                            for i, comment in enumerate(chat['similar_comments'][:3], 1):
                                st.write(f"**{i}.** {comment['comment'][:150]}...")
                                st.caption(f"Kategori: {comment['category']}, Öncelik: {comment['priority_score']:.0f}/100, Benzerlik: {comment['similarity']:.2f}")
                        
                        if chat.get('knowledge_results'):
                            st.subheader("📚 Bilgi Tabanı")
                            for i, kb in enumerate(chat['knowledge_results'], 1):
                                st.write(f"**{i}. {kb['category'].title()}**")
                                st.write(f"Problem: {kb['problem']}")
                                st.write(f"Çözüm: {kb['solution']}")
                                st.caption(f"Benzerlik: {kb['similarity']:.2f}")
    
    with tab2:
        st.header("🔍 Gelişmiş Arama")
        
        search_query = st.text_input(
            "Arama terimi:",
            placeholder="Örn: kargo gecikme, kalite sorunu"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            search_count = st.slider("Sonuç sayısı:", 1, 10, 5)
        with col2:
            search_type = st.selectbox("Arama tipi:", ["Yorumlar", "Bilgi Tabanı", "Her ikisi"])
        
        if st.button("🔍 Ara") and search_query:
            with st.spinner("Aranıyor..."):
                
                if search_type in ["Yorumlar", "Her ikisi"]:
                    st.subheader("📝 Benzer Yorumlar")
                    similar_comments = st.session_state.rag_system.search_similar_comments(search_query, search_count)
                    
                    if similar_comments:
                        for i, comment in enumerate(similar_comments, 1):
                            with st.expander(f"Yorum {i} - Benzerlik: {comment['similarity']:.2f}"):
                                st.write(f"**Kullanıcı:** {comment['user']}")
                                st.write(f"**Tarih:** {comment['date']}")
                                st.write(f"**Kategori:** {comment['category']}")
                                st.write(f"**Öncelik:** {comment['priority_score']:.0f}/100")
                                st.write(f"**Yorum:** {comment['comment']}")
                    else:
                        st.info("Benzer yorum bulunamadı.")
                
                if search_type in ["Bilgi Tabanı", "Her ikisi"]:
                    st.subheader("📚 Bilgi Tabanı Sonuçları")
                    kb_results = st.session_state.rag_system.search_knowledge_base(search_query, search_count)
                    
                    if kb_results:
                        for i, kb in enumerate(kb_results, 1):
                            with st.expander(f"Bilgi {i} - {kb['category'].title()} - Benzerlik: {kb['similarity']:.2f}"):
                                st.write(f"**Problem:** {kb['problem']}")
                                st.write(f"**Çözüm:** {kb['solution']}")
                                if kb['keywords']:
                                    st.write(f"**Anahtar Kelimeler:** {', '.join(kb['keywords'])}")
                    else:
                        st.info("İlgili bilgi bulunamadı.")
    
    with tab3:
        st.header("📊 Detaylı Analiz")
        
        if st.button("🔄 Analizi Yenile"):
            stats = st.session_state.rag_system.get_stats()
            
            # Genel istatistikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam Yorum", stats['total_comments'])
            with col2:
                st.metric("Bilgi Girdisi", stats['total_knowledge_entries'])
            with col3:
                st.metric("Ortalama Öncelik", f"{stats['average_priority']:.1f}")
            with col4:
                st.metric("Analiz Modülleri", "Aktif" if stats['has_advanced_analyzers'] else "Pasif")
            
            # Kategori analizi
            if stats['category_distribution']:
                st.subheader("📈 Kategori Dağılımı")
                
                category_df = pd.DataFrame(
                    list(stats['category_distribution'].items()),
                    columns=['Kategori', 'Sayı']
                )
                category_df['Yüzde'] = (category_df['Sayı'] / category_df['Sayı'].sum() * 100).round(1)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(category_df.set_index('Kategori')['Sayı'])
                
                with col2:
                    st.dataframe(category_df, hide_index=True)
            
            # Sistem bilgileri
            st.subheader("🔧 Sistem Bilgileri")
            st.json({
                "Python Sürümü": "3.13",
                "RAG Tipi": "TF-IDF Tabanlı",
                "Veritabanı": "SQLite",
                "Dependency": "Minimal",
                "Analiz Modülleri": stats['has_advanced_analyzers']
            })

else:
    # Sistem kurulmamışsa
    st.warning("⚠️ Lütfen önce RAG sistemini başlatın.")
    
    st.markdown("""
    ## 🚀 Başlangıç Rehberi
    
    1. **📊 Sol panel**: "RAG Sistemini Başlat" butonuna tıklayın
    2. **📁 CSV dosyası**: `trendyol_comments.csv` otomatik yüklenecek
    3. **💬 Chat**: Yorumlar hakkında soru sorun
    4. **🔍 Arama**: Gelişmiş filtreleme yapın
    
    ### 💡 Örnek Sorular:
    
    - "Kargo sorunları hakkında ne tür şikayetler var?"
    - "En çok şikayet alan kategori hangisi?"
    - "Kalite konusunda nasıl iyileştirme yapabiliriz?"
    - "Müşteri memnuniyetini artırmak için öneriler"
    
    ### ✨ Özellikler:
    
    - 🎯 **TF-IDF Benzerlik**: Keyword'lerden daha akıllı arama
    - 📚 **Bilgi Tabanı**: Çözüm önerileri ile entegre
    - 📊 **Analiz Modülleri**: Mevcut sistem entegrasyonu
    - 🚀 **Python 3.13 Uyumlu**: Modern Python desteği
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🛍️ <strong>Trendyol RAG Chat</strong> - Basit ve Güçlü Yorum Analizi<br>
    🚀 <em>Python 3.13 • TF-IDF • Minimal Dependency</em>
</div>
""", unsafe_allow_html=True) 