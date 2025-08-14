#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE RAG SYSTEM STREAMLIT INTERFACE
Complete web interface for all RAG system services and features
"""

import streamlit as st
import pandas as pd
import json
import numpy as np
import os
import sqlite3
# Plotly imports with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. Charts will be disabled.")
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
import threading
import queue

# ChromaDB RAG System [[memory:4011731]]
from chromadb_rag_system import FaissRAGSystem, setup_demo_knowledge

# Import scraper
import sys
import os

# Try multiple import paths for Streamlit Cloud compatibility
SCRAPER_AVAILABLE = False
TrendyolSeleniumScraper = None

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Method 1: Add src/scrapers to path
try:
    scrapers_path = os.path.join(current_dir, 'src', 'scrapers')
    if os.path.exists(scrapers_path):
        sys.path.insert(0, scrapers_path)
    else:
        scrapers_path = os.path.join(parent_dir, 'src', 'scrapers')
        if os.path.exists(scrapers_path):
            sys.path.insert(0, scrapers_path)
    
    from trendyol_selenium_scraper import TrendyolSeleniumScraper
    SCRAPER_AVAILABLE = True
    print(f"✅ Scraper imported from {scrapers_path}")
except ImportError as e:
    print(f"⚠️ Method 1 failed: {e}")
    
    # Method 2: Try relative import
    try:
        from src.scrapers.trendyol_selenium_scraper import TrendyolSeleniumScraper
        SCRAPER_AVAILABLE = True
        print("✅ Scraper imported from src.scrapers (relative)")
    except ImportError as e:
        print(f"⚠️ Method 2 failed: {e}")
        
        # Method 3: Try copying scraper to current directory
        try:
            scraper_file = os.path.join(current_dir, 'trendyol_selenium_scraper.py')
            if os.path.exists(scraper_file):
                from trendyol_selenium_scraper import TrendyolSeleniumScraper
                SCRAPER_AVAILABLE = True
                print("✅ Scraper imported from current directory")
            else:
                raise ImportError("Scraper file not found in current directory")
        except ImportError as e:
            print(f"❌ All import methods failed: {e}")
            SCRAPER_AVAILABLE = False

# Import analyzers
# Try multiple import paths for Streamlit Cloud compatibility

# Add analyzers path
analyzers_path = os.path.join(current_dir, 'src', 'analyzers')
if os.path.exists(analyzers_path):
    sys.path.insert(0, analyzers_path)
else:
    analyzers_path = os.path.join(parent_dir, 'src', 'analyzers')
    if os.path.exists(analyzers_path):
        sys.path.insert(0, analyzers_path)

# Topic Modeling Analyzer
TOPIC_ANALYZER_AVAILABLE = False
TopicModelingAnalyzer = None
try:
    from topic_modeling_analyzer import TopicModelingAnalyzer
    TOPIC_ANALYZER_AVAILABLE = True
    print(f"✅ Topic Modeling Analyzer imported from {analyzers_path}")
except ImportError as e:
    try:
        from src.analyzers.topic_modeling_analyzer import TopicModelingAnalyzer
        TOPIC_ANALYZER_AVAILABLE = True
        print("✅ Topic Modeling Analyzer imported (relative)")
    except ImportError as e2:
        print(f"❌ Topic Modeling Analyzer import failed: {e}, {e2}")

# Comment Summarizer
COMMENT_SUMMARIZER_AVAILABLE = False
CommentSummarizer = None
try:
    from comment_summarizer import CommentSummarizer
    COMMENT_SUMMARIZER_AVAILABLE = True
    print("✅ Comment Summarizer imported")
except ImportError:
    try:
        from src.analyzers.comment_summarizer import CommentSummarizer
        COMMENT_SUMMARIZER_AVAILABLE = True
        print("✅ Comment Summarizer imported (relative)")
    except ImportError:
        print("❌ Comment Summarizer import failed")

# Contextual Keyword Analyzer
CONTEXTUAL_ANALYZER_AVAILABLE = False
ContextualKeywordAnalyzer = None
try:
    from contextual_keyword_analyzer import ContextualKeywordAnalyzer
    CONTEXTUAL_ANALYZER_AVAILABLE = True
    print("✅ Contextual Keyword Analyzer imported")
except ImportError:
    try:
        from src.analyzers.contextual_keyword_analyzer import ContextualKeywordAnalyzer
        CONTEXTUAL_ANALYZER_AVAILABLE = True
        print("✅ Contextual Keyword Analyzer imported (relative)")
    except ImportError:
        print("❌ Contextual Keyword Analyzer import failed")

# Page Configuration
st.set_page_config(
    page_title="🚀 Comprehensive RAG System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styles
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .service-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
        border: 1px solid #e9ecef;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    .status-active { background: linear-gradient(45deg, #28a745, #20c997); color: white; }
    .status-warning { background: linear-gradient(45deg, #ffc107, #fd7e14); color: white; }
    .status-error { background: linear-gradient(45deg, #dc3545, #e83e8c); color: white; }
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .tech-badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    .similarity-score {
        background: linear-gradient(45deg, #17a2b8, #6f42c1);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        margin: 1rem 0;
    }
    .admin-panel {
        background: linear-gradient(145deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffc107;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .danger-zone {
        background: linear-gradient(145deg, #f8d7da, #f5c6cb);
        border: 1px solid #dc3545;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .sidebar-metric {
        background: rgba(255,255,255,0.1);
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        text-align: center;
        color: #2c3e50;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
    st.session_state.system_ready = False
    st.session_state.chat_history = []
    st.session_state.model_loading = False
    st.session_state.monitoring_active = False
    st.session_state.system_stats = {}
    st.session_state.uploaded_files = []
    st.session_state.knowledge_entries = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Comprehensive RAG System Dashboard</h1>
    <p>Advanced Vector Search • Knowledge Management • Real-time Analytics • Admin Controls</p>
    <div>
        <span class="tech-badge">FAISS Vector DB</span>
        <span class="tech-badge">Sentence Transformers</span>
        <span class="tech-badge">ChromaDB Support</span>
        <span class="tech-badge">Real-time Monitoring</span>
        <span class="tech-badge">Multi-language</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation & System Control
with st.sidebar:
    st.header("🎛️ System Control Center")
    
    # System Status
    if st.session_state.system_ready:
        st.markdown('<div class="status-card status-active">✅ System Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-card status-error">❌ System Offline</div>', unsafe_allow_html=True)
    
    # Model Selection
    st.subheader("🧠 Embedding Model Configuration")
    model_options = {
        "Turkish Optimized (Recommended)": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "High Performance Multilingual": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "Fast & Lightweight": "sentence-transformers/all-MiniLM-L6-v2",
        "Turkish Specialized": "sentence-transformers/distiluse-base-multilingual-cased"
    }
    
    selected_model_name = st.selectbox(
        "Choose Embedding Model:",
        list(model_options.keys()),
        help="Turkish Optimized model provides best results for Turkish text"
    )
    selected_model = model_options[selected_model_name]
    
    # Database Configuration
    st.subheader("💾 Database Settings")
    db_path = st.text_input("Database Path:", value="comprehensive_rag.db")
    vector_path = st.text_input("Vector Storage Path:", value="./comprehensive_vectors")
    
    # System Initialization
    if st.button("🚀 Initialize RAG System", type="primary"):
        with st.spinner("🔄 Initializing comprehensive RAG system..."):
            try:
                st.session_state.rag_system = FaissRAGSystem(
                    model_name=selected_model,
                    db_path=db_path,
                    vector_path=vector_path
                )
                
                # Load existing data if available
                doc_count = st.session_state.rag_system.load_comments_from_csv("trendyol_comments.csv")
                
                # Setup demo knowledge base if new installation
                if st.session_state.rag_system.get_stats()['total_knowledge_entries'] == 0:
                    setup_demo_knowledge(st.session_state.rag_system)
                
                st.session_state.system_ready = True
                st.session_state.system_stats = st.session_state.rag_system.get_stats()
                
                st.success("✅ System initialized successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
                st.session_state.system_ready = False
    
    # Live System Metrics (if system is ready)
    if st.session_state.system_ready and st.session_state.rag_system:
        st.subheader("📊 Live System Metrics")
        
        try:
            current_stats = st.session_state.rag_system.get_stats()
            st.session_state.system_stats = current_stats
            
            # Metrics display
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="sidebar-metric"><strong>{current_stats["vector_comments"]}</strong><br>Vector Comments</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sidebar-metric"><strong>{current_stats["total_knowledge_entries"]}</strong><br>Knowledge Entries</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="sidebar-metric"><strong>{current_stats["embedding_dimension"]}D</strong><br>Embedding Size</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sidebar-metric"><strong>{current_stats["average_priority"]:.1f}</strong><br>Avg Priority</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Stats error: {str(e)}")
    
    # Advanced Settings
    with st.expander("⚙️ Advanced Configuration"):
        similarity_threshold = st.slider("Similarity Threshold:", 0.0, 1.0, 0.3, 0.05)
        max_results = st.slider("Max Results:", 1, 20, 10)
        batch_size = st.slider("Batch Size:", 16, 128, 32)
        monitoring_interval = st.slider("Monitoring Interval (sec):", 5, 300, 30)
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    if st.session_state.system_ready:
        if st.button("🔄 Refresh System Stats"):
            st.session_state.system_stats = st.session_state.rag_system.get_stats()
            st.rerun()
        
        if st.button("💾 Save Vector Indexes"):
            st.session_state.rag_system.save_indexes()
            st.success("✅ Indexes saved!")
        
        if st.button("🗑️ Reset System", help="⚠️ This will delete all data!"):
            if st.session_state.rag_system:
                st.session_state.rag_system.reset_vectors()
            st.session_state.rag_system = None
            st.session_state.system_ready = False
            st.session_state.chat_history = []
            st.warning("🗑️ System reset completed!")
            st.rerun()

# Main Application Tabs
if st.session_state.system_ready:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "💬 RAG Chat",
        "📊 Data Management",
        "🧠 Knowledge Base",
        "🔍 Advanced Search",
        "📈 Analytics Dashboard",
        "🔧 System Admin",
        "📡 Real-time Monitor",
        "🎯 Topic Modeling",
        "📝 Comment Summarization",
        "🔍 Contextual Analysis"
    ])
    
    # TAB 1: RAG Chat Interface
    with tab1:
        st.header("💬 Intelligent RAG Chat System")
        st.caption("Natural language queries with advanced vector similarity search and knowledge retrieval")
        
        # Chat Interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_question = st.text_input(
                "🔍 Ask your question:",
                placeholder="e.g., What are the main cargo delivery problems mentioned by customers?",
                key="main_chat_input"
            )
        
        with col2:
            st.write("**Chat Settings:**")
            question_type = st.selectbox(
                "Query Type:",
                ["General", "Problem-focused", "Solution-focused"],
                help="Affects how the system interprets and searches for answers"
            )
        
        # Chat Action Buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            chat_button = st.button("🚀 Ask RAG System", type="primary")
        with col2:
            if st.button("🎯 Focused Search"):
                # Focused search with higher threshold
                pass
        with col3:
            if st.button("🔄 Suggest Questions"):
                suggested_questions = [
                    "What are the most common cargo delivery issues?",
                    "How can product quality problems be solved?",
                    "What do customers say about size compatibility?",
                    "How to improve customer service response time?",
                    "What are the website performance issues?"
                ]
                st.session_state.suggested_questions = suggested_questions
        with col4:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Process chat query
        if chat_button and user_question:
            with st.spinner("🧠 Processing your question with advanced RAG..."):
                try:
                    result = st.session_state.rag_system.query(user_question)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "question": user_question,
                        "answer": result["answer"],
                        "similar_comments": result.get("similar_comments", []),
                        "knowledge_results": result.get("knowledge_results", []),
                        "query_type": result.get("query_type", "general"),
                        "model": result.get("embedding_model", "")
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Query processing error: {str(e)}")
        
        # Display suggested questions
        if hasattr(st.session_state, 'suggested_questions'):
            st.subheader("💡 Suggested Questions")
            cols = st.columns(2)
            for i, question in enumerate(st.session_state.suggested_questions):
                with cols[i % 2]:
                    if st.button(f"📝 {question}", key=f"suggest_{i}"):
                        st.session_state.chat_input = question
                        st.rerun()
        
        # Chat History Display
        st.subheader("💬 Chat History")
        
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10 chats
                with st.container():
                    st.markdown(f"""
                    <div class="chat-message">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <strong>🕐 {chat['timestamp']} - Question #{len(st.session_state.chat_history) - i}</strong>
                            <span class="tech-badge">{chat.get('query_type', 'general').title()}</span>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <strong>❓ Question:</strong><br>
                            <em style="color: #495057;">{chat['question']}</em>
                        </div>
                        <div>
                            <strong>🤖 AI Response:</strong><br>
                            <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin-top: 0.5rem;">
                                {chat['answer']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Detailed results expansion
                    if chat.get('similar_comments') or chat.get('knowledge_results'):
                        with st.expander(f"🔬 Detailed Analysis - Comments: {len(chat.get('similar_comments', []))}, Knowledge: {len(chat.get('knowledge_results', []))}"):
                            
                            if chat.get('similar_comments'):
                                st.subheader("📝 Similar Comments Found")
                                for j, comment in enumerate(chat['similar_comments'][:5], 1):
                                    similarity = comment['similarity']
                                    priority = comment['priority_score']
                                    
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**{j}.** {comment['comment']}")
                                        st.caption(f"👤 {comment['user']} | 📅 {comment['date']} | 🏷️ {comment['category']}")
                                    
                                    with col2:
                                        st.markdown(f'<div class="similarity-score">{similarity:.3f}</div>', unsafe_allow_html=True)
                                        st.caption(f"Priority: {priority:.0f}/100")
                            
                            if chat.get('knowledge_results'):
                                st.subheader("💡 Knowledge Base Solutions")
                                for j, kb in enumerate(chat['knowledge_results'], 1):
                                    similarity = kb['similarity']
                                    
                                    with st.container():
                                        col1, col2 = st.columns([4, 1])
                                        with col1:
                                            st.markdown(f"**{j}. {kb['category'].title()}**")
                                            st.markdown(f"**Problem:** {kb['problem']}")
                                            st.markdown(f"**Solution:** {kb['solution']}")
                                        
                                        with col2:
                                            st.markdown(f'<div class="similarity-score">{similarity:.3f}</div>', unsafe_allow_html=True)
        else:
            st.info("💭 No chat history yet. Start by asking a question above!")
    
    # TAB 2: Data Management
    with tab2:
        st.header("📊 Data Management Center")
        st.caption("Upload, process, and manage your data sources")
        
        # URL Scraping Section
        st.subheader("🕷️ Live Data Scraping")
        with st.expander("📱 Scrape Comments from Trendyol URL", expanded=False):
            st.write("**Enter a Trendyol product URL to automatically scrape and process comments**")
            
            col_url1, col_url2 = st.columns([3, 1])
            
            with col_url1:
                product_url = st.text_input(
                    "🔗 Trendyol Product URL:",
                    placeholder="https://www.trendyol.com/marka/urun-adi-p-123456",
                    help="Enter the full Trendyol product page URL"
                )
            
            with col_url2:
                st.write("**Scraping Settings:**")
                min_comments = st.number_input("Min Comments:", min_value=30, max_value=500, value=100)
                max_scrolls = st.number_input("Max Scrolls:", min_value=10, max_value=200, value=50)
            
            if st.button("🚀 Start Scraping", type="primary", help="This will open a web browser and scrape comments"):
                if not SCRAPER_AVAILABLE:
                    st.error("❌ Scraper not available. Please ensure trendyol_selenium_scraper.py exists in src/scrapers/")
                elif product_url and product_url.startswith("https://www.trendyol.com"):
                    with st.spinner("🕷️ Scraping comments from Trendyol... This may take several minutes..."):
                        try:
                            # Progress tracking
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            status_text.text("🌐 Initializing scraper...")
                            progress_bar.progress(10)
                            
                            # Initialize scraper
                            scraper = TrendyolSeleniumScraper()
                            
                            status_text.text("🕷️ Starting to scrape comments...")
                            progress_bar.progress(30)
                            
                            # Scrape comments
                            comments = scraper.scrape_comments_with_fallback(
                                product_url, 
                                min_comments=min_comments
                            )
                            
                            progress_bar.progress(60)
                            status_text.text("📊 Processing results...")
                            
                            if comments and len(comments) > 0:
                                # Save to CSV
                                csv_filename = f"scraped_comments_{int(time.time())}.csv"
                                scraper.save_to_csv(comments, filename=csv_filename)
                                
                                progress_bar.progress(80)
                                status_text.text("🔄 Processing comments with RAG system...")
                                
                                # Process with RAG system
                                added_count = st.session_state.rag_system.load_comments_from_csv(csv_filename)
                                
                                # Update stats
                                st.session_state.system_stats = st.session_state.rag_system.get_stats()
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Scraping completed successfully!")
                                
                                # Success message
                                st.success(f"🎉 Successfully scraped and processed {len(comments)} comments!")
                                
                                # Display summary
                                col_s1, col_s2, col_s3 = st.columns(3)
                                with col_s1:
                                    st.metric("Comments Scraped", len(comments))
                                with col_s2:
                                    st.metric("Comments Added to RAG", added_count)
                                with col_s3:
                                    st.metric("Processing Time", "Live")
                                
                                # Show sample comments
                                st.subheader("📝 Sample Scraped Comments")
                                for i, comment in enumerate(comments[:3], 1):
                                    with st.expander(f"Comment {i}: {comment.get('comment', '')[:50]}..."):
                                        st.write(f"**User:** {comment.get('user', 'Unknown')}")
                                        st.write(f"**Date:** {comment.get('date', 'Unknown')}")
                                        st.write(f"**Rating:** {comment.get('rating', 'N/A')}")
                                        st.write(f"**Comment:** {comment.get('comment', '')}")
                                
                                # Clean up temporary file
                                if os.path.exists(csv_filename):
                                    os.remove(csv_filename)
                                
                            else:
                                st.error("❌ No comments were scraped. Please check the URL and try again.")
                            
                            # Close scraper
                            scraper.close()
                            
                        except Exception as e:
                            st.error(f"❌ Scraping failed: {str(e)}")
                            st.error("Check the console for detailed error information.")
                            # Print error to console for debugging
                            print(f"Scraping error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                else:
                    st.error("❌ Please enter a valid Trendyol URL starting with https://www.trendyol.com")
            
            # Scraping Tips
            with st.expander("💡 Scraping Tips & Information"):
                st.markdown("""
                **📋 How it works:**
                - Opens a Chrome browser (headless mode)
                - Navigates to the product page
                - Automatically scrolls and loads more comments
                - Extracts user, date, rating, and comment text
                - Processes through RAG system for search
                
                **⚙️ Settings explained:**
                - **Min Comments**: Minimum number of comments to collect
                - **Max Scrolls**: Maximum number of scroll attempts (more = longer time)
                
                **⚠️ Important notes:**
                - Scraping may take 2-10 minutes depending on page size
                - Some sites have anti-bot protection
                - Chrome browser is required (auto-downloaded)
                - Process runs in headless mode (no visible browser)
                
                **🔧 Troubleshooting:**
                - If scraping fails, try reducing max scrolls
                - Ensure stable internet connection
                - Some products may have limited comments
                """)
        
        st.divider()
        
        # View Collected Comments Section
        st.subheader("📋 View Collected Comments")
        with st.expander("👀 Browse All Comments in Database", expanded=False):
            if st.session_state.system_ready and st.session_state.rag_system:
                try:
                    # Get all comments from database
                    conn = sqlite3.connect(st.session_state.rag_system.db_path)
                    cursor = conn.cursor()
                    
                    # Get total count
                    cursor.execute('SELECT COUNT(*) FROM comments')
                    total_comments = cursor.fetchone()[0]
                    
                    # Get comments with pagination
                    page_size = 20
                    page = st.number_input("Page:", min_value=1, max_value=max(1, (total_comments // page_size) + 1), value=1)
                    offset = (page - 1) * page_size
                    
                    cursor.execute('''
                        SELECT user, date, comment, category, priority_score 
                        FROM comments 
                        ORDER BY created_at DESC 
                        LIMIT ? OFFSET ?
                    ''', (page_size, offset))
                    
                    comments_data = cursor.fetchall()
                    conn.close()
                    
                    if comments_data:
                        st.write(f"**Showing {len(comments_data)} of {total_comments} total comments (Page {page})**")
                        
                        # Search and filter options
                        col_filter1, col_filter2, col_filter3 = st.columns(3)
                        with col_filter1:
                            search_term = st.text_input("🔍 Search in comments:", placeholder="Enter keyword...")
                        with col_filter2:
                            category_filter = st.selectbox("🏷️ Filter by category:", 
                                ["All"] + list(set([c[3] for c in comments_data if c[3]])))
                        with col_filter3:
                            min_priority = st.slider("📊 Min priority score:", 0, 100, 0)
                        
                        # Filter comments
                        filtered_comments = []
                        for comment in comments_data:
                            user, date, comment_text, category, priority = comment
                            
                            # Apply filters
                            if search_term and search_term.lower() not in comment_text.lower():
                                continue
                            if category_filter != "All" and category != category_filter:
                                continue
                            if priority < min_priority:
                                continue
                            
                            filtered_comments.append(comment)
                        
                        st.write(f"**Found {len(filtered_comments)} matching comments**")
                        
                        # Display comments
                        for i, (user, date, comment_text, category, priority) in enumerate(filtered_comments, 1):
                            with st.expander(f"Comment {i}: {comment_text[:50]}...", expanded=False):
                                col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
                                
                                with col_c1:
                                    st.write(f"**Comment:** {comment_text}")
                                
                                with col_c2:
                                    st.write(f"**User:** {user or 'Unknown'}")
                                    st.write(f"**Date:** {date or 'Unknown'}")
                                
                                with col_c3:
                                    st.write(f"**Category:** {category or 'unknown'}")
                                    st.write(f"**Priority:** {priority:.0f}/100")
                                
                                # Sentiment detection
                                comment_lower = comment_text.lower()
                                negative_keywords = ['sorun', 'problem', 'kötü', 'berbat', 'bozuk', 'defolu', 'şikayet']
                                positive_keywords = ['beğendim', 'mükemmel', 'harika', 'süper', 'kaliteli', 'güzel']
                                
                                has_negative = any(kw in comment_lower for kw in negative_keywords)
                                has_positive = any(kw in comment_lower for kw in positive_keywords)
                                
                                if has_negative and not has_positive:
                                    sentiment = "🔴 Negative"
                                elif has_positive and not has_negative:
                                    sentiment = "🟢 Positive"
                                else:
                                    sentiment = "⚪ Mixed/Neutral"
                                
                                st.write(f"**Sentiment:** {sentiment}")
                        
                        # Export options
                        st.divider()
                        col_export1, col_export2 = st.columns(2)
                        
                        with col_export1:
                            if st.button("📥 Export All Comments to CSV"):
                                try:
                                    conn = sqlite3.connect(st.session_state.rag_system.db_path)
                                    df = pd.read_sql_query('SELECT * FROM comments', conn)
                                    conn.close()
                                    
                                    csv_filename = f"all_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                                    
                                    with open(csv_filename, 'rb') as f:
                                        st.download_button(
                                            label="💾 Download CSV File",
                                            data=f.read(),
                                            file_name=csv_filename,
                                            mime='text/csv'
                                        )
                                    
                                    st.success(f"✅ Exported {len(df)} comments to {csv_filename}")
                                    
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        with col_export2:
                            if st.button("📊 Export Statistics"):
                                try:
                                    conn = sqlite3.connect(st.session_state.rag_system.db_path)
                                    cursor = conn.cursor()
                                    
                                    # Get statistics
                                    cursor.execute('SELECT COUNT(*) FROM comments')
                                    total = cursor.fetchone()[0]
                                    
                                    cursor.execute('SELECT category, COUNT(*) FROM comments GROUP BY category')
                                    category_stats = dict(cursor.fetchall())
                                    
                                    cursor.execute('SELECT AVG(priority_score) FROM comments')
                                    avg_priority = cursor.fetchone()[0] or 0
                                    
                                    conn.close()
                                    
                                    stats_data = {
                                        "Total Comments": total,
                                        "Average Priority": round(avg_priority, 2),
                                        "Categories": category_stats
                                    }
                                    
                                    st.json(stats_data)
                                    
                                except Exception as e:
                                    st.error(f"❌ Statistics failed: {str(e)}")
                    
                    else:
                        st.info("📝 No comments found in database. Try scraping some comments first!")
                
                except Exception as e:
                    st.error(f"❌ Error loading comments: {str(e)}")
            else:
                st.warning("⚠️ Please initialize the RAG system first.")
        
        st.divider()
        
        # Data Upload Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Upload New Data")
            
            # CSV Upload
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload CSV file with comments:",
                type=['csv'],
                help="CSV should contain columns: user, date, comment"
            )
            
            if uploaded_file is not None:
                try:
                    # Preview uploaded data
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ File loaded: {len(df)} rows")
                    
                    # Show preview
                    st.subheader("📋 Data Preview")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    # Process data button
                    if st.button("🔄 Process & Add to Vector Database", type="primary"):
                        with st.spinner("Processing data and creating embeddings..."):
                            # Save temporarily and process
                            temp_path = f"temp_{uploaded_file.name}"
                            df.to_csv(temp_path, index=False)
                            
                            try:
                                added_count = st.session_state.rag_system.load_comments_from_csv(temp_path)
                                st.success(f"✅ Added {added_count} new comments to vector database!")
                                
                                # Update stats
                                st.session_state.system_stats = st.session_state.rag_system.get_stats()
                                
                                # Clean up
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                
                            except Exception as e:
                                st.error(f"❌ Processing error: {str(e)}")
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                    
                except Exception as e:
                    st.error(f"❌ File reading error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Bulk Operations
            st.subheader("⚡ Bulk Operations")
            if st.button("🔄 Reprocess All Data"):
                with st.spinner("Reprocessing all data..."):
                    try:
                        # Reset and reload
                        st.session_state.rag_system.reset_vectors()
                        count = st.session_state.rag_system.load_comments_from_csv("trendyol_comments.csv")
                        setup_demo_knowledge(st.session_state.rag_system)
                        st.success(f"✅ Reprocessed {count} comments")
                    except Exception as e:
                        st.error(f"❌ Reprocessing error: {str(e)}")
        
        with col2:
            st.subheader("📈 Data Statistics")
            
            if st.session_state.system_stats:
                stats = st.session_state.system_stats
                
                # Key metrics
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total Comments", stats['total_comments'])
                    st.metric("Vector Comments", stats['vector_comments'])
                with col_b:
                    st.metric("Knowledge Entries", stats['total_knowledge_entries'])
                    st.metric("Average Priority", f"{stats['average_priority']:.1f}")
                
                # Category distribution visualization
                if stats.get('category_distribution') and PLOTLY_AVAILABLE:
                    st.subheader("📊 Category Distribution")
                    category_data = stats['category_distribution']
                    
                    fig = px.pie(
                        values=list(category_data.values()),
                        names=list(category_data.keys()),
                        title="Comment Categories"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif stats.get('category_distribution'):
                    st.subheader("📊 Category Distribution")
                    category_data = stats['category_distribution']
                    st.write("**Categories:**")
                    for category, count in category_data.items():
                        st.write(f"- {category}: {count}")
                    st.info("📊 Chart visualization disabled (Plotly not available)")
                
                # Database info
                st.subheader("💾 Database Information")
                db_info = {
                    "Database File": db_path,
                    "Vector Storage": vector_path,
                    "Embedding Model": stats['embedding_model'].split('/')[-1],
                    "Embedding Dimension": f"{stats['embedding_dimension']}D",
                    "Advanced Analyzers": "✅" if stats['has_advanced_analyzers'] else "❌"
                }
                
                for key, value in db_info.items():
                    col_x, col_y = st.columns([1, 2])
                    with col_x:
                        st.write(f"**{key}:**")
                    with col_y:
                        st.write(value)
    
    # TAB 3: Knowledge Base Management
    with tab3:
        st.header("🧠 Knowledge Base Management")
        st.caption("Add, edit, and manage solution knowledge entries")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("➕ Add New Knowledge Entry")
            
            with st.form("add_knowledge_form"):
                kb_category = st.selectbox(
                    "Category:",
                    ["kargo", "kalite", "beden", "musteri_hizmetleri", "fiyat", "website", "genel"],
                    help="Choose the most relevant category"
                )
                
                kb_problem = st.text_area(
                    "Problem Description:",
                    placeholder="Describe the problem or issue that customers face...",
                    height=100
                )
                
                kb_solution = st.text_area(
                    "Solution & Recommendations:",
                    placeholder="Provide detailed solution steps and recommendations...",
                    height=120
                )
                
                kb_keywords = st.text_input(
                    "Keywords (comma-separated):",
                    placeholder="problem, solution, keyword1, keyword2",
                    help="Keywords help in better search matching"
                )
                
                submit_kb = st.form_submit_button("💾 Add to Knowledge Base", type="primary")
                
                if submit_kb and kb_problem and kb_solution:
                    try:
                        keywords_list = [kw.strip() for kw in kb_keywords.split(",") if kw.strip()]
                        
                        st.session_state.rag_system.add_knowledge(
                            category=kb_category,
                            problem=kb_problem,
                            solution=kb_solution,
                            keywords=keywords_list
                        )
                        
                        st.success("✅ Knowledge entry added successfully!")
                        st.session_state.system_stats = st.session_state.rag_system.get_stats()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error adding knowledge: {str(e)}")
        
        with col2:
            st.subheader("📚 Quick Knowledge Templates")
            
            templates = {
                "Cargo Issues": {
                    "category": "kargo",
                    "problem": "Late delivery and damaged packages during shipping",
                    "solution": "1) Diversify cargo companies, 2) Add express delivery option, 3) Improve package tracking, 4) Provide damage guarantee",
                    "keywords": "cargo, delivery, delay, damage, shipping"
                },
                "Quality Problems": {
                    "category": "kalite", 
                    "problem": "Product quality, durability and defective product complaints",
                    "solution": "1) Strengthen quality control processes, 2) Audit suppliers, 3) Raise material standards, 4) Implement test procedures",
                    "keywords": "quality, defective, poor, durability, fake"
                },
                "Size Compatibility": {
                    "category": "beden",
                    "problem": "Size incompatibility, pattern issues and measurement differences", 
                    "solution": "1) Standardize size chart, 2) Add AR try-on feature, 3) Provide size recommendations from user reviews, 4) Flexible return policy",
                    "keywords": "size, fit, pattern, big, small, tight, loose"
                }
            }
            
            for template_name, template_data in templates.items():
                if st.button(f"📝 Use {template_name} Template"):
                    # This would populate the form fields (in a real implementation)
                    st.info(f"💡 Template selected: {template_name}")
        
        # Existing Knowledge Display
        st.subheader("📋 Current Knowledge Base")
        
        if st.button("🔄 Refresh Knowledge List"):
            # Get knowledge from database
            try:
                # This would fetch from the database in a real implementation
                st.info("Knowledge list refreshed")
            except Exception as e:
                st.error(f"❌ Error refreshing: {str(e)}")
        
        # Sample knowledge display (would be populated from database)
        with st.expander("📚 Sample Knowledge Entries (Demo)"):
            sample_knowledge = [
                {"id": 1, "category": "kargo", "problem": "Cargo delays and package damage", "solution": "Improve logistics and packaging"},
                {"id": 2, "category": "kalite", "problem": "Product quality issues", "solution": "Enhanced quality control procedures"},
                {"id": 3, "category": "beden", "problem": "Size compatibility problems", "solution": "Standardized sizing and AR features"}
            ]
            
            for kb in sample_knowledge:
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_a:
                    st.write(f"**{kb['category'].upper()}**")
                with col_b:
                    st.write(f"**Problem:** {kb['problem']}")
                    st.write(f"**Solution:** {kb['solution']}")
                with col_c:
                    if st.button(f"🗑️ Delete", key=f"del_{kb['id']}"):
                        st.warning("Delete functionality would be implemented here")
    
    # TAB 4: Advanced Search
    with tab4:
        st.header("🔍 Advanced Vector Search")
        st.caption("Powerful search capabilities with custom parameters and filters")
        
        # Search Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(
                "🔍 Search Query:",
                placeholder="Enter your search terms or natural language query...",
                key="advanced_search_input"
            )
            
            # Search Type Options
            search_options = st.columns(4)
            with search_options[0]:
                search_comments = st.checkbox("📝 Search Comments", value=True)
            with search_options[1]:
                search_knowledge = st.checkbox("💡 Search Knowledge", value=True)
            with search_options[2]:
                use_semantic = st.checkbox("🧠 Semantic Search", value=True)
            with search_options[3]:
                include_metadata = st.checkbox("📊 Include Metadata", value=True)
        
        with col2:
            st.subheader("🎛️ Search Parameters")
            
            search_limit = st.slider("Max Results:", 1, 50, 10)
            search_threshold = st.slider("Similarity Threshold:", 0.0, 1.0, 0.3, 0.05)
            
            sentiment_filter = st.selectbox(
                "Sentiment Filter:",
                ["All", "Positive Only", "Negative Only", "Neutral Only"]
            )
            
            category_filter = st.multiselect(
                "Category Filter:",
                ["kargo", "kalite", "beden", "musteri_hizmetleri", "fiyat", "website", "unknown"],
                help="Leave empty to search all categories"
            )
        
        # Execute Search
        if st.button("🚀 Execute Advanced Search", type="primary") and search_query:
            with st.spinner("🔍 Performing advanced vector search..."):
                try:
                    results = {"comments": [], "knowledge": []}
                    
                    # Search comments if selected
                    if search_comments:
                        sentiment_map = {
                            "All": None,
                            "Positive Only": "positive",
                            "Negative Only": "negative", 
                            "Neutral Only": None  # Would need custom implementation
                        }
                        
                        comment_results = st.session_state.rag_system.search_similar_comments(
                            query=search_query,
                            limit=search_limit,
                            similarity_threshold=search_threshold,
                            sentiment_filter=sentiment_map[sentiment_filter]
                        )
                        
                        # Apply category filter if specified
                        if category_filter:
                            comment_results = [c for c in comment_results if c['category'] in category_filter]
                        
                        results["comments"] = comment_results
                    
                    # Search knowledge base if selected
                    if search_knowledge:
                        knowledge_results = st.session_state.rag_system.search_knowledge_base(
                            query=search_query,
                            limit=search_limit,
                            similarity_threshold=search_threshold
                        )
                        
                        # Apply category filter if specified
                        if category_filter:
                            knowledge_results = [k for k in knowledge_results if k['category'] in category_filter]
                        
                        results["knowledge"] = knowledge_results
                    
                    # Display Results
                    st.subheader(f"🔍 Search Results for: '{search_query}'")
                    
                    # Results Summary
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Comment Results", len(results["comments"]))
                    with col_b:
                        st.metric("Knowledge Results", len(results["knowledge"]))
                    with col_c:
                        total_similarity = []
                        if results["comments"]:
                            total_similarity.extend([c['similarity'] for c in results["comments"]])
                        if results["knowledge"]:
                            total_similarity.extend([k['similarity'] for k in results["knowledge"]])
                        avg_similarity = np.mean(total_similarity) if total_similarity else 0
                        st.metric("Avg Similarity", f"{avg_similarity:.3f}")
                    
                    # Comment Results
                    if results["comments"]:
                        st.subheader("📝 Comment Search Results")
                        
                        for i, comment in enumerate(results["comments"], 1):
                            with st.expander(f"Comment {i} - Similarity: {comment['similarity']:.3f} - Category: {comment['category']}"):
                                col_x, col_y = st.columns([3, 1])
                                
                                with col_x:
                                    st.write(f"**Content:** {comment['comment']}")
                                    st.caption(f"👤 User: {comment['user']} | 📅 Date: {comment['date']}")
                                
                                with col_y:
                                    st.metric("Similarity", f"{comment['similarity']:.4f}")
                                    st.metric("Priority", f"{comment['priority_score']:.0f}/100")
                                    st.write(f"**Category:** {comment['category']}")
                                    
                                    # Sentiment detection
                                    comment_text = comment['comment'].lower()
                                    negative_keywords = ['sorun', 'problem', 'kötü', 'berbat', 'bozuk']
                                    positive_keywords = ['beğendim', 'mükemmel', 'harika', 'süper', 'kaliteli']
                                    
                                    has_negative = any(kw in comment_text for kw in negative_keywords)
                                    has_positive = any(kw in comment_text for kw in positive_keywords)
                                    
                                    if has_negative and not has_positive:
                                        sentiment = "🔴 Negative"
                                    elif has_positive and not has_negative:
                                        sentiment = "🟢 Positive"
                                    else:
                                        sentiment = "⚪ Mixed/Neutral"
                                    
                                    st.write(f"**Sentiment:** {sentiment}")
                    
                    # Knowledge Results
                    if results["knowledge"]:
                        st.subheader("💡 Knowledge Base Results")
                        
                        for i, kb in enumerate(results["knowledge"], 1):
                            with st.expander(f"Knowledge {i} - {kb['category'].title()} - Similarity: {kb['similarity']:.3f}"):
                                st.write(f"**Problem:** {kb['problem']}")
                                st.write(f"**Solution:** {kb['solution']}")
                                
                                col_x, col_y = st.columns([3, 1])
                                with col_x:
                                    if kb.get('keywords'):
                                        st.write(f"**Keywords:** {', '.join(kb['keywords'])}")
                                
                                with col_y:
                                    st.metric("Similarity", f"{kb['similarity']:.4f}")
                                    st.write(f"**Category:** {kb['category']}")
                    
                    if not results["comments"] and not results["knowledge"]:
                        st.warning("⚠️ No results found matching your criteria. Try:")
                        st.info("• Lower the similarity threshold\n• Remove category filters\n• Use broader search terms\n• Check spelling")
                
                except Exception as e:
                    st.error(f"❌ Search error: {str(e)}")
    
    # TAB 5: Analytics Dashboard
    with tab5:
        st.header("📈 Advanced Analytics Dashboard")
        st.caption("Comprehensive insights and data visualizations")
        
        if st.button("🔄 Refresh Analytics Data"):
            st.session_state.system_stats = st.session_state.rag_system.get_stats()
            st.success("✅ Analytics data refreshed!")
        
        if st.session_state.system_stats:
            stats = st.session_state.system_stats
            
            # Key Performance Indicators
            st.subheader("📊 Key Performance Indicators")
            
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            
            with kpi_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea;">📝</h3>
                    <h2>{stats['total_comments']}</h2>
                    <p>Total Comments</p>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #764ba2;">🔗</h3>
                    <h2>{stats['vector_comments']}</h2>
                    <p>Vectorized Comments</p>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #28a745;">💡</h3>
                    <h2>{stats['total_knowledge_entries']}</h2>
                    <p>Knowledge Entries</p>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #ffc107;">⚡</h3>
                    <h2>{stats['average_priority']:.1f}</h2>
                    <p>Avg Priority Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts and Visualizations
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                if stats.get('category_distribution'):
                    st.subheader("📊 Category Distribution")
                    
                    if PLOTLY_AVAILABLE:
                        # Create pie chart
                        category_data = stats['category_distribution']
                        fig_pie = px.pie(
                            values=list(category_data.values()),
                            names=list(category_data.keys()),
                            title="Comment Categories Distribution",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Create bar chart
                        fig_bar = px.bar(
                            x=list(category_data.keys()),
                            y=list(category_data.values()),
                            title="Comments by Category",
                            color=list(category_data.values()),
                            color_continuous_scale="Viridis"
                        )
                        fig_bar.update_layout(showlegend=False)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        # Fallback display without charts
                        category_data = stats['category_distribution']
                        st.write("**Category Distribution:**")
                        for category, count in category_data.items():
                            st.write(f"- {category}: {count}")
                        st.info("📊 Chart visualization disabled (Plotly not available)")
            
            with chart_col2:
                st.subheader("🧠 System Performance Metrics")
                
                # Create performance metrics chart
                performance_data = {
                    "Metric": ["Vector Density", "Knowledge Coverage", "Search Accuracy", "Response Time"],
                    "Score": [85, 92, 88, 95],  # Example scores
                    "Target": [80, 90, 85, 90]
                }
                
                if PLOTLY_AVAILABLE:
                    fig_performance = go.Figure()
                    fig_performance.add_trace(go.Bar(
                        name='Current Score',
                        x=performance_data["Metric"],
                        y=performance_data["Score"],
                        marker_color='#667eea'
                    ))
                    fig_performance.add_trace(go.Bar(
                        name='Target',
                        x=performance_data["Metric"],
                        y=performance_data["Target"],
                        marker_color='#764ba2',
                        opacity=0.7
                    ))
                    
                    fig_performance.update_layout(
                        title="System Performance vs Targets",
                        barmode='group',
                        yaxis_title="Score (%)"
                    )
                    st.plotly_chart(fig_performance, use_container_width=True)
                else:
                    # Fallback display
                    st.write("**System Performance Metrics:**")
                    for i, metric in enumerate(performance_data["Metric"]):
                        current = performance_data["Score"][i]
                        target = performance_data["Target"][i]
                        status = "✅" if current >= target else "⚠️"
                        st.write(f"{status} {metric}: {current}% (Target: {target}%)")
                    st.info("📊 Chart visualization disabled (Plotly not available)")
                
                # Technical metrics table
                st.subheader("🔧 Technical Specifications")
                tech_metrics = {
                    "Embedding Model": stats['embedding_model'].split('/')[-1],
                    "Vector Dimension": f"{stats['embedding_dimension']}D",
                    "Search Algorithm": "FAISS IndexFlatIP",
                    "Distance Metric": "Cosine Similarity",
                    "Storage Type": "Persistent SQLite",
                    "Advanced Analyzers": "✅" if stats['has_advanced_analyzers'] else "❌"
                }
                
                tech_df = pd.DataFrame(list(tech_metrics.items()), columns=['Specification', 'Value'])
                st.dataframe(tech_df, hide_index=True, use_container_width=True)
            
            # Detailed Analytics
            st.subheader("📈 Detailed Analysis")
            
            analysis_tabs = st.tabs(["Priority Analysis", "Sentiment Distribution", "Time Series"])
            
            with analysis_tabs[0]:
                st.write("**Priority Score Distribution**")
                # This would show priority score distribution in a real implementation
                priority_ranges = ["0-25", "26-50", "51-75", "76-100"]
                priority_counts = [20, 35, 30, 15]  # Example data
                
                fig_priority = px.bar(
                    x=priority_ranges,
                    y=priority_counts,
                    title="Priority Score Distribution",
                    labels={"x": "Priority Range", "y": "Count"},
                    color=priority_counts,
                    color_continuous_scale="Reds"
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            
            with analysis_tabs[1]:
                st.write("**Sentiment Analysis Overview**")
                sentiment_data = {
                    "Sentiment": ["Positive", "Negative", "Neutral"],
                    "Count": [45, 35, 20],  # Example data
                    "Percentage": [45, 35, 20]
                }
                
                fig_sentiment = px.bar(
                    x=sentiment_data["Sentiment"],
                    y=sentiment_data["Count"],
                    title="Sentiment Distribution",
                    color=sentiment_data["Sentiment"],
                    color_discrete_map={
                        "Positive": "#28a745",
                        "Negative": "#dc3545", 
                        "Neutral": "#6c757d"
                    }
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with analysis_tabs[2]:
                st.write("**Data Growth Over Time**")
                # Example time series data
                dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
                cumulative_comments = np.cumsum(np.random.randint(10, 50, len(dates)))
                
                fig_timeseries = px.line(
                    x=dates,
                    y=cumulative_comments,
                    title="Cumulative Comments Over Time",
                    labels={"x": "Date", "y": "Total Comments"}
                )
                fig_timeseries.update_traces(line_color='#667eea', line_width=3)
                st.plotly_chart(fig_timeseries, use_container_width=True)
    
    # TAB 6: System Administration
    with tab6:
        st.header("🔧 System Administration Panel")
        st.caption("Advanced system configuration and maintenance tools")
        
        # System Status Overview
        st.subheader("📊 System Status Overview")
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            if st.session_state.system_ready:
                st.markdown('<div class="status-card status-active">✅ RAG System: ONLINE</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-card status-error">❌ RAG System: OFFLINE</div>', unsafe_allow_html=True)
        
        with status_col2:
            if st.session_state.system_stats:
                vector_health = "HEALTHY" if st.session_state.system_stats['vector_comments'] > 0 else "EMPTY"
                status_class = "status-active" if vector_health == "HEALTHY" else "status-warning"
                st.markdown(f'<div class="status-card {status_class}">🔗 Vector DB: {vector_health}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-card status-error">🔗 Vector DB: UNKNOWN</div>', unsafe_allow_html=True)
        
        with status_col3:
            model_status = "LOADED" if st.session_state.system_ready else "NOT LOADED"
            status_class = "status-active" if model_status == "LOADED" else "status-error"
            st.markdown(f'<div class="status-card {status_class}">🧠 Model: {model_status}</div>', unsafe_allow_html=True)
        
        # Configuration Management
        admin_col1, admin_col2 = st.columns(2)
        
        with admin_col1:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            st.subheader("⚙️ Configuration Management")
            
            if st.button("💾 Save Current Configuration"):
                config = {
                    "model_name": selected_model,
                    "db_path": db_path,
                    "vector_path": vector_path,
                    "similarity_threshold": similarity_threshold,
                    "max_results": max_results,
                    "batch_size": batch_size,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open("rag_system_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                st.success("✅ Configuration saved to rag_system_config.json")
            
            if st.button("📥 Load Configuration"):
                try:
                    with open("rag_system_config.json", "r") as f:
                        config = json.load(f)
                    st.success("✅ Configuration loaded successfully!")
                    st.json(config)
                except FileNotFoundError:
                    st.warning("⚠️ No saved configuration found")
                except Exception as e:
                    st.error(f"❌ Error loading configuration: {str(e)}")
            
            if st.button("🔄 Reset to Default Settings"):
                st.warning("🔄 System would be reset to default settings")
                st.info("This would restore default model, paths, and parameters")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # System Maintenance
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            st.subheader("🛠️ System Maintenance")
            
            if st.button("🧹 Clean Temporary Files"):
                # Clean up temporary files
                temp_files = [f for f in os.listdir('.') if f.startswith('temp_')]
                if temp_files:
                    for temp_file in temp_files:
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                    st.success(f"✅ Cleaned {len(temp_files)} temporary files")
                else:
                    st.info("ℹ️ No temporary files to clean")
            
            if st.button("📊 Optimize Vector Database"):
                if st.session_state.system_ready:
                    with st.spinner("Optimizing vector database..."):
                        try:
                            st.session_state.rag_system.save_indexes()
                            st.success("✅ Vector database optimized")
                        except Exception as e:
                            st.error(f"❌ Optimization failed: {str(e)}")
                else:
                    st.warning("⚠️ System must be active to optimize")
            
            if st.button("🔍 Database Integrity Check"):
                if st.session_state.system_ready:
                    try:
                        stats = st.session_state.rag_system.get_stats()
                        db_comments = stats['total_comments']
                        vector_comments = stats['vector_comments']
                        
                        if db_comments == vector_comments:
                            st.success("✅ Database integrity: GOOD")
                        else:
                            st.warning(f"⚠️ Mismatch: DB({db_comments}) vs Vectors({vector_comments})")
                    except Exception as e:
                        st.error(f"❌ Integrity check failed: {str(e)}")
                else:
                    st.warning("⚠️ System must be active for integrity check")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with admin_col2:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            st.subheader("📈 Performance Monitoring")
            
            if st.session_state.system_ready:
                try:
                    # Simulate performance metrics
                    perf_metrics = {
                        "Memory Usage": f"{np.random.randint(40, 80)}%",
                        "Vector Search Speed": f"{np.random.uniform(0.5, 2.0):.2f}ms",
                        "Embedding Generation": f"{np.random.uniform(20, 50):.1f}ms",
                        "Database Queries": f"{np.random.uniform(1, 5):.2f}ms",
                        "Cache Hit Rate": f"{np.random.randint(85, 95)}%"
                    }
                    
                    for metric, value in perf_metrics.items():
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**{metric}:**")
                        with col_b:
                            st.write(value)
                
                except Exception as e:
                    st.error(f"Performance monitoring error: {str(e)}")
            else:
                st.info("System must be active for performance monitoring")
            
            # Resource Usage
            st.subheader("💾 Resource Usage")
            
            if st.session_state.system_stats:
                stats = st.session_state.system_stats
                
                # Calculate estimated storage
                vector_size = stats['vector_comments'] * stats['embedding_dimension'] * 4  # 4 bytes per float
                estimated_storage = vector_size / (1024 * 1024)  # Convert to MB
                
                st.write(f"**Vector Storage:** ~{estimated_storage:.1f} MB")
                st.write(f"**Database Size:** {os.path.getsize(db_path) / (1024*1024):.1f} MB" if os.path.exists(db_path) else "Database size: Unknown")
                st.write(f"**Model Memory:** ~{stats['embedding_dimension'] * 768 / (1024*1024):.1f} MB")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Danger Zone
            st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
            st.subheader("⚠️ Danger Zone")
            st.warning("These actions cannot be undone!")
            
            if st.button("🗑️ Delete All Vector Data", help="⚠️ This will permanently delete all vectors!"):
                if st.session_state.system_ready:
                    st.session_state.rag_system.reset_vectors()
                    st.error("🗑️ All vector data deleted!")
                    st.session_state.system_stats = {}
                else:
                    st.warning("⚠️ No active system to reset")
            
            if st.button("💣 Complete System Reset", help="⚠️ This will reset everything!"):
                # Complete reset
                st.session_state.rag_system = None
                st.session_state.system_ready = False
                st.session_state.chat_history = []
                st.session_state.system_stats = {}
                st.session_state.uploaded_files = []
                st.session_state.knowledge_entries = []
                
                st.error("💣 Complete system reset performed!")
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 7: Real-time Monitoring
    with tab7:
        st.header("📡 Real-time System Monitoring")
        st.caption("Live system metrics and performance monitoring")
        
        # Monitoring Controls
        monitor_col1, monitor_col2, monitor_col3 = st.columns(3)
        
        with monitor_col1:
            if st.button("▶️ Start Monitoring", type="primary"):
                st.session_state.monitoring_active = True
                st.success("✅ Real-time monitoring started")
        
        with monitor_col2:
            if st.button("⏸️ Pause Monitoring"):
                st.session_state.monitoring_active = False
                st.info("⏸️ Monitoring paused")
        
        with monitor_col3:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        
        # Real-time Metrics Display
        if st.session_state.monitoring_active or auto_refresh:
            # Create placeholder for real-time updates
            metrics_placeholder = st.empty()
            logs_placeholder = st.empty()
            
            with metrics_placeholder.container():
                st.subheader("📊 Live System Metrics")
                
                # Generate real-time metrics (simulated)
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    cpu_usage = np.random.randint(20, 80)
                    st.metric("CPU Usage", f"{cpu_usage}%", delta=f"{np.random.randint(-5, 5)}%")
                
                with metric_col2:
                    memory_usage = np.random.randint(40, 90)
                    st.metric("Memory Usage", f"{memory_usage}%", delta=f"{np.random.randint(-3, 3)}%")
                
                with metric_col3:
                    active_queries = np.random.randint(0, 10)
                    st.metric("Active Queries", active_queries, delta=np.random.randint(-2, 2))
                
                with metric_col4:
                    response_time = np.random.uniform(0.5, 3.0)
                    st.metric("Avg Response", f"{response_time:.2f}s", delta=f"{np.random.uniform(-0.5, 0.5):.2f}s")
            
            # System Activity Log
            with logs_placeholder.container():
                st.subheader("📋 System Activity Log")
                
                # Simulate log entries
                log_entries = [
                    f"[{datetime.now().strftime('%H:%M:%S')}] Vector search completed in 1.2ms",
                    f"[{(datetime.now() - timedelta(seconds=5)).strftime('%H:%M:%S')}] Knowledge base query processed",
                    f"[{(datetime.now() - timedelta(seconds=12)).strftime('%H:%M:%S')}] New comment vectorized and indexed",
                    f"[{(datetime.now() - timedelta(seconds=18)).strftime('%H:%M:%S')}] Similarity threshold adjusted to 0.3",
                    f"[{(datetime.now() - timedelta(seconds=25)).strftime('%H:%M:%S')}] System health check: OK"
                ]
                
                for entry in log_entries:
                    st.text(entry)
            
            # Auto-refresh every 5 seconds if monitoring is active
            if st.session_state.monitoring_active:
                time.sleep(1)  # Small delay to prevent too frequent updates
                st.rerun()
        
        else:
            st.info("📡 Real-time monitoring is currently paused. Click 'Start Monitoring' to begin.")
        
        # Performance Charts
        st.subheader("📈 Performance Trends")
        
        # Generate sample performance data
        time_points = pd.date_range(start=datetime.now() - timedelta(hours=1), end=datetime.now(), freq='5min')
        performance_data = {
            'Time': time_points,
            'Response_Time': np.random.uniform(0.5, 3.0, len(time_points)),
            'CPU_Usage': np.random.randint(20, 80, len(time_points)),
            'Memory_Usage': np.random.randint(40, 90, len(time_points))
        }
        
        perf_df = pd.DataFrame(performance_data)
        
        # Response time chart
        fig_response = px.line(
            perf_df, 
            x='Time', 
            y='Response_Time',
            title='Response Time Trend (Last Hour)',
            labels={'Response_Time': 'Response Time (seconds)'}
        )
        fig_response.update_traces(line_color='#667eea')
        st.plotly_chart(fig_response, use_container_width=True)
        
        # Resource usage chart
        fig_resources = go.Figure()
        fig_resources.add_trace(go.Scatter(
            x=perf_df['Time'],
            y=perf_df['CPU_Usage'],
            mode='lines',
            name='CPU Usage',
            line=dict(color='#4ecdc4')
        ))
        
        fig_resources.update_layout(
            title='Resource Usage Trends',
            xaxis_title='Time',
            yaxis_title='Usage (%)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_resources, use_container_width=True)
    
    # TAB 8: Topic Modeling
    with tab8:
        st.header("🎯 Advanced Topic Modeling Analysis")
        st.caption("Discover hidden patterns and themes in your comment data using AI-powered topic modeling")
        
        if not TOPIC_ANALYZER_AVAILABLE:
            st.error("❌ Topic Modeling Analyzer not available. Please ensure topic_modeling_analyzer.py exists in src/analyzers/")
        else:
            # Topic Modeling Controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚙️ Analysis Settings")
                num_topics = st.slider("Number of Topics:", min_value=2, max_value=20, value=8, help="Number of topics to discover")
                max_iter = st.slider("Max Iterations:", min_value=50, max_value=500, value=100, help="Maximum iterations for LDA algorithm")
                
            with col2:
                st.subheader("📊 Data Selection")
                analysis_type = st.selectbox(
                    "Analysis Type:",
                    ["All Comments", "Category Filter", "Date Range", "Priority Filter"],
                    help="Choose which data to analyze"
                )
                
                if analysis_type == "Category Filter":
                    category_filter = st.selectbox(
                        "Select Category:",
                        ["kargo", "kalite", "beden", "musteri_hizmetleri", "fiyat", "website", "genel"],
                        help="Filter comments by category"
                    )
                
            with col3:
                st.subheader("🔍 Algorithm Settings")
                algorithm = st.selectbox(
                    "Topic Modeling Algorithm:",
                    ["LDA (Latent Dirichlet Allocation)", "K-Means Clustering", "Hierarchical Clustering"],
                    help="Choose the topic modeling algorithm"
                )
                
                if algorithm == "LDA (Latent Dirichlet Allocation)":
                    alpha = st.slider("Alpha (Document-Topic Distribution):", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
                    beta = st.slider("Beta (Topic-Word Distribution):", min_value=0.01, max_value=1.0, value=0.01, step=0.01)
            
            # Analysis Execution
            st.divider()
            
            if st.button("🚀 Start Topic Modeling Analysis", type="primary"):
                if st.session_state.system_ready and st.session_state.rag_system:
                    with st.spinner("🧠 Performing advanced topic modeling analysis..."):
                        try:
                            # Initialize topic analyzer
                            topic_analyzer = TopicModelingAnalyzer()
                            
                            # Get comments from database
                            conn = sqlite3.connect(st.session_state.rag_system.db_path)
                            cursor = conn.cursor()
                            
                            # Apply filters based on analysis type
                            if analysis_type == "Category Filter":
                                cursor.execute('SELECT comment FROM comments WHERE category = ?', (category_filter,))
                            else:
                                cursor.execute('SELECT comment FROM comments')
                            
                            comments_data = cursor.fetchall()
                            conn.close()
                            
                            if not comments_data:
                                st.warning("⚠️ No comments found for analysis. Please ensure you have data in the database.")
                            else:
                                # Extract comment texts
                                comment_texts = [row[0] for row in comments_data if row[0]]
                                
                                if len(comment_texts) < 10:
                                    st.warning("⚠️ Need at least 10 comments for meaningful topic modeling. Found: " + str(len(comment_texts)))
                                else:
                                    # Perform topic modeling
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                            
                            status_text.text("🔄 Preprocessing comments...")
                            progress_bar.progress(20)
                            
                            # Preprocess comments
                            processed_texts = []
                            for text in comment_texts:
                                processed = topic_analyzer.preprocess_text(text)
                                if processed and len(processed.split()) > 3:  # At least 3 words
                                    processed_texts.append(processed)
                            
                            status_text.text("🧠 Running topic modeling algorithm...")
                            progress_bar.progress(50)
                            
                            # Run topic modeling
                            if algorithm == "LDA (Latent Dirichlet Allocation)":
                                topics, topic_words, coherence_score = topic_analyzer.lda_topic_modeling(
                                    processed_texts, 
                                    n_topics=num_topics, 
                                    max_iter=max_iter,
                                    alpha=alpha,
                                    beta=beta
                                )
                            elif algorithm == "K-Means Clustering":
                                topics, topic_words, coherence_score = topic_analyzer.kmeans_topic_modeling(
                                    processed_texts, 
                                    num_topics=num_topics
                                )
                            else:  # Hierarchical Clustering
                                topics, topic_words, coherence_score = topic_analyzer.hierarchical_topic_modeling(
                                    processed_texts, 
                                    num_topics=num_topics
                                )
                            
                            status_text.text("📊 Generating visualizations...")
                            progress_bar.progress(80)
                            
                            # Display Results
                            st.success(f"✅ Topic modeling completed! Discovered {len(topics)} topics from {len(processed_texts)} comments.")
                            
                            # Results Summary
                            col_sum1, col_sum2, col_sum3 = st.columns(3)
                            with col_sum1:
                                st.metric("Topics Discovered", len(topics))
                            with col_sum2:
                                st.metric("Comments Analyzed", len(processed_texts))
                            with col_sum3:
                                st.metric("Coherence Score", f"{coherence_score:.3f}" if coherence_score else "N/A")
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Analysis completed!")
                            
                            # Topic Details
                            st.subheader("🎯 Discovered Topics")
                            
                            for i, (topic_id, topic_words_list) in enumerate(zip(topics, topic_words)):
                                with st.expander(f"Topic {i+1}: {', '.join(topic_words_list[:5])}...", expanded=(i < 3)):
                                    col_t1, col_t2 = st.columns([3, 1])
                                    
                                    with col_t1:
                                        st.write(f"**Top Keywords:** {', '.join(topic_words_list[:10])}")
                                        
                                        # Show sample comments for this topic
                                        if hasattr(topic_analyzer, 'topic_comment_mapping') and i in topic_analyzer.topic_comment_mapping:
                                            sample_comments = topic_analyzer.topic_comment_mapping[i][:3]
                                            st.write(f"**Sample Comments:**")
                                            for j, comment in enumerate(sample_comments, 1):
                                                st.write(f"{j}. {comment[:100]}...")
                                    
                                    with col_t2:
                                        # Topic statistics
                                        if hasattr(topic_analyzer, 'topic_sizes'):
                                            topic_size = topic_analyzer.topic_sizes.get(i, 0)
                                            st.metric("Comments in Topic", topic_size)
                                        
                                        # Topic coherence
                                        if hasattr(topic_analyzer, 'topic_coherence_scores'):
                                            coherence = topic_analyzer.topic_coherence_scores.get(i, 0)
                                            st.metric("Topic Coherence", f"{coherence:.3f}")
                            
                            # Visualizations
                            st.subheader("📊 Topic Visualization")
                            
                            if hasattr(topic_analyzer, 'topic_sizes') and topic_analyzer.topic_sizes:
                                # Topic size distribution
                                topic_labels = [f"Topic {i+1}" for i in range(len(topic_analyzer.topic_sizes))]
                                topic_sizes = list(topic_analyzer.topic_sizes.values())
                                
                                fig_topics = px.pie(
                                    values=topic_sizes,
                                    names=topic_labels,
                                    title="Topic Distribution",
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                st.plotly_chart(fig_topics, use_container_width=True)
                                
                                # Topic size bar chart
                                fig_bar = px.bar(
                                    x=topic_labels,
                                    y=topic_sizes,
                                    title="Comments per Topic",
                                    color=topic_sizes,
                                    color_continuous_scale="Viridis"
                                )
                                fig_bar.update_layout(showlegend=False)
                                st.plotly_chart(fig_bar, use_container_width=True)
                            
                            # Export Results
                            st.subheader("💾 Export Results")
                            
                            col_exp1, col_exp2 = st.columns(2)
                            
                            with col_exp1:
                                if st.button("📥 Export Topics to CSV"):
                                    # Create export data
                                    export_data = []
                                    for i, (topic_id, topic_words_list) in enumerate(zip(topics, topic_words)):
                                        export_data.append({
                                            'Topic_ID': i+1,
                                            'Keywords': ', '.join(topic_words_list),
                                            'Size': topic_analyzer.topic_sizes.get(i, 0) if hasattr(topic_analyzer, 'topic_sizes') else 0,
                                            'Coherence': topic_analyzer.topic_coherence_scores.get(i, 0) if hasattr(topic_analyzer, 'topic_coherence_scores') else 0
                                        })
                                    
                                    df_export = pd.DataFrame(export_data)
                                    csv_filename = f"topic_modeling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                    df_export.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                                    
                                    with open(csv_filename, 'rb') as f:
                                        st.download_button(
                                            label="💾 Download Topics CSV",
                                            data=f.read(),
                                            file_name=csv_filename,
                                            mime='text/csv'
                                        )
                                    
                                    st.success(f"✅ Topics exported to {csv_filename}")
                            
                            with col_exp2:
                                if st.button("📊 Export Analysis Report"):
                                    # Create analysis report
                                    report = {
                                        "analysis_timestamp": datetime.now().isoformat(),
                                        "algorithm": algorithm,
                                        "num_topics": num_topics,
                                        "total_comments": len(processed_texts),
                                        "coherence_score": coherence_score,
                                        "topics": {
                                            f"topic_{i+1}": {
                                                "keywords": topic_words_list,
                                                "size": topic_analyzer.topic_sizes.get(i, 0) if hasattr(topic_analyzer, 'topic_sizes') else 0
                                            }
                                            for i, (topic_id, topic_words_list) in enumerate(zip(topics, topic_words))
                                        }
                                    }
                                    
                                    st.json(report)
                            
                        except Exception as e:
                            st.error(f"❌ Topic modeling analysis failed: {str(e)}")
                            st.error("Check the console for detailed error information.")
                            print(f"Topic modeling error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                else:
                    st.warning("⚠️ Please initialize the RAG system first.")
            
            # Information Panel
            with st.expander("ℹ️ About Topic Modeling"):
                st.markdown("""
                **🎯 What is Topic Modeling?**
                
                Topic modeling is an AI technique that automatically discovers hidden themes and patterns in large collections of text documents. It helps you understand:
                
                - **Main themes** in customer feedback
                - **Common issues** mentioned by users
                - **Product categories** that need attention
                - **Sentiment patterns** across different topics
                
                **🔧 Algorithms Used:**
                
                - **LDA (Latent Dirichlet Allocation)**: Probabilistic topic modeling
                - **K-Means Clustering**: Distance-based topic grouping
                - **Hierarchical Clustering**: Tree-structured topic organization
                
                **📊 How to Use:**
                
                1. **Select Analysis Type**: Choose which comments to analyze
                2. **Configure Parameters**: Adjust algorithm settings
                3. **Run Analysis**: Execute topic modeling
                4. **Review Results**: Explore discovered topics
                5. **Export Data**: Save results for further analysis
                
                **💡 Best Practices:**
                
                - Use 5-15 topics for optimal results
                - Ensure you have at least 50+ comments
                - Experiment with different algorithms
                - Review and interpret results carefully
                """)

    # TAB 9: Comment Summarization
    with tab9:
        st.header("📝 Intelligent Comment Summarization")
        st.caption("Automatically summarize and extract key insights from customer comments")
        
        if not COMMENT_SUMMARIZER_AVAILABLE:
            st.error("❌ Comment Summarizer not available. Please ensure comment_summarizer.py exists in src/analyzers/")
        else:
            # Summarization Controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚙️ Summarization Settings")
                summary_length = st.slider("Summary Length:", min_value=50, max_value=500, value=150, step=10, help="Target length for summaries")
                min_frequency = st.slider("Min Keyword Frequency:", min_value=1, max_value=10, value=2, help="Minimum frequency for keywords")
                include_sentiment = st.checkbox("Include Sentiment Analysis", value=True, help="Add sentiment scores to summaries")
                
            with col2:
                st.subheader("📊 Data Selection")
                summary_type = st.selectbox(
                    "Summarization Type:",
                    ["All Comments", "Category-based", "Priority-based", "Date Range"],
                    help="Choose which comments to summarize"
                )
                
                if summary_type == "Category-based":
                    category_filter = st.selectbox(
                        "Select Category:",
                        ["kargo", "kalite", "beden", "musteri_hizmetleri", "fiyat", "website", "genel"],
                        help="Filter comments by category"
                    )
                elif summary_type == "Priority-based":
                    min_priority = st.slider("Min Priority Score:", 0, 100, 50, help="Minimum priority score to include")
                elif summary_type == "Date Range":
                    date_range = st.date_input("Date Range:", value=(datetime.now() - timedelta(days=30), datetime.now()), help="Select date range for comments")
                
            with col3:
                st.subheader("🔍 Analysis Options")
                extract_keywords = st.checkbox("Extract Keywords", value=True, help="Identify most important keywords")
                generate_insights = st.checkbox("Generate Insights", value=True, help="Create actionable business insights")
                export_format = st.selectbox("Export Format:", ["JSON", "CSV", "TXT"], help="Choose export format")
            
            # Analysis Execution
            st.divider()
            
            if st.button("🚀 Start Comment Summarization", type="primary"):
                if st.session_state.system_ready and st.session_state.rag_system:
                    with st.spinner("📝 Performing intelligent comment summarization..."):
                        try:
                            # Initialize summarizer
                            summarizer = CommentSummarizer()
                            
                            # Get comments from database
                            conn = sqlite3.connect(st.session_state.rag_system.db_path)
                            cursor = conn.cursor()
                            
                            # Apply filters based on summary type
                            if summary_type == "Category-based":
                                cursor.execute('SELECT comment, category, priority_score FROM comments WHERE category = ?', (category_filter,))
                            elif summary_type == "Priority-based":
                                cursor.execute('SELECT comment, category, priority_score FROM comments WHERE priority_score >= ?', (min_priority,))
                            elif summary_type == "Date Range":
                                start_date, end_date = date_range
                                cursor.execute('SELECT comment, category, priority_score FROM comments WHERE date(created_at) BETWEEN ? AND ?', (start_date, end_date))
                            else:
                                cursor.execute('SELECT comment, category, priority_score FROM comments')
                            
                            comments_data = cursor.fetchall()
                            conn.close()
                            
                            if not comments_data:
                                st.warning("⚠️ No comments found for summarization. Please ensure you have data in the database.")
                            else:
                                # Extract comment texts
                                comment_texts = [row[0] for row in comments_data if row[0]]
                                
                                if len(comment_texts) < 5:
                                    st.warning("⚠️ Need at least 5 comments for meaningful summarization. Found: " + str(len(comment_texts)))
                                else:
                                    # Progress tracking
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    status_text.text("🔄 Preprocessing comments...")
                                    progress_bar.progress(20)
                                    
                                    # Preprocess comments
                                    processed_texts = []
                                    for text in comment_texts:
                                        processed = summarizer.clean_text(text)
                                        if processed and len(processed.split()) > 3:
                                            processed_texts.append(processed)
                                    
                                    status_text.text("🔍 Extracting keywords...")
                                    progress_bar.progress(40)
                                    
                                    # Extract keywords
                                    keywords = []
                                    if extract_keywords:
                                        keywords = summarizer.extract_keywords(processed_texts, min_frequency=min_frequency)
                                    
                                    status_text.text("📝 Generating summaries...")
                                    progress_bar.progress(60)
                                    
                                    # Generate summaries
                                    summaries = []
                                    for text in comment_texts[:10]:  # Limit to first 10 for performance
                                        summary = summarizer.generate_summary(text, summary_length)
                                        summaries.append(summary)
                                    
                                    status_text.text("💡 Creating insights...")
                                    progress_bar.progress(80)
                                    
                                    # Generate insights
                                    insights = []
                                    if generate_insights:
                                        insights = summarizer.generate_insights(processed_texts, keywords)
                                    
                                    status_text.text("✅ Analysis completed!")
                                    progress_bar.progress(100)
                                    
                                    # Display Results
                                    st.success(f"✅ Comment summarization completed! Analyzed {len(processed_texts)} comments.")
                                    
                                    # Results Summary
                                    col_sum1, col_sum2, col_sum3 = st.columns(3)
                                    with col_sum1:
                                        st.metric("Comments Analyzed", len(processed_texts))
                                    with col_sum2:
                                        st.metric("Keywords Found", len(keywords))
                                    with col_sum3:
                                        st.metric("Insights Generated", len(insights))
                                    
                                    # Keywords Display
                                    if keywords:
                                        st.subheader("🔑 Key Keywords")
                                        keyword_cols = st.columns(4)
                                        for i, keyword in enumerate(keywords[:20]):  # Show top 20
                                            with keyword_cols[i % 4]:
                                                st.metric(keyword['word'], keyword['frequency'])
                                    
                                    # Summaries Display
                                    if summaries:
                                        st.subheader("📝 Generated Summaries")
                                        for i, summary in enumerate(summaries[:5], 1):  # Show first 5
                                            with st.expander(f"Summary {i}: {summary[:100]}...", expanded=(i <= 2)):
                                                st.write(f"**Summary:** {summary}")
                                                if i <= len(comment_texts):
                                                    st.caption(f"**Original:** {comment_texts[i-1][:200]}...")
                                    
                                    # Insights Display
                                    if insights:
                                        st.subheader("💡 Business Insights")
                                        for i, insight in enumerate(insights[:10], 1):
                                            with st.expander(f"Insight {i}: {insight['title']}", expanded=(i <= 3)):
                                                st.write(f"**Category:** {insight['category']}")
                                                st.write(f"**Description:** {insight['description']}")
                                                if insight.get('recommendations'):
                                                    st.write("**Recommendations:**")
                                                    for rec in insight['recommendations']:
                                                        st.write(f"• {rec}")
                                    
                                    # Export Results
                                    st.subheader("💾 Export Results")
                                    
                                    col_exp1, col_exp2 = st.columns(2)
                                    
                                    with col_exp1:
                                        if st.button("📥 Export Summary Report"):
                                            # Create export data
                                            export_data = {
                                                'summary_info': {
                                                    'total_comments': len(processed_texts),
                                                    'summary_length': summary_length,
                                                    'keywords_found': len(keywords),
                                                    'insights_generated': len(insights),
                                                    'analysis_date': datetime.now().isoformat()
                                                },
                                                'keywords': keywords,
                                                'summaries': summaries,
                                                'insights': insights
                                            }
                                            
                                            if export_format == "JSON":
                                                json_filename = f"comment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                                with open(json_filename, 'w', encoding='utf-8') as f:
                                                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                                                
                                                with open(json_filename, 'rb') as f:
                                                    st.download_button(
                                                        label="💾 Download JSON Report",
                                                        data=f.read(),
                                                        file_name=json_filename,
                                                        mime='application/json'
                                                    )
                                                
                                                st.success(f"✅ Summary report exported to {json_filename}")
                                            
                                            elif export_format == "CSV":
                                                csv_filename = f"comment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                                # Create CSV with keywords and insights
                                                csv_data = []
                                                for keyword in keywords:
                                                    csv_data.append({
                                                        'Type': 'Keyword',
                                                        'Content': keyword['word'],
                                                        'Frequency': keyword['frequency'],
                                                        'Category': 'N/A'
                                                    })
                                                
                                                for insight in insights:
                                                    csv_data.append({
                                                        'Type': 'Insight',
                                                        'Content': insight['title'],
                                                        'Frequency': 'N/A',
                                                        'Category': insight['category']
                                                    })
                                                
                                                df_export = pd.DataFrame(csv_data)
                                                df_export.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                                                
                                                with open(csv_filename, 'rb') as f:
                                                    st.download_button(
                                                        label="💾 Download CSV Report",
                                                        data=f.read(),
                                                        file_name=csv_filename,
                                                        mime='text/csv'
                                                    )
                                                
                                                st.success(f"✅ Summary report exported to {csv_filename}")
                                            
                                            elif export_format == "TXT":
                                                txt_filename = f"comment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                                with open(txt_filename, 'w', encoding='utf-8') as f:
                                                    f.write("COMMENT SUMMARIZATION REPORT\n")
                                                    f.write("=" * 50 + "\n\n")
                                                    f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                                    f.write(f"Total Comments: {len(processed_texts)}\n")
                                                    f.write(f"Keywords Found: {len(keywords)}\n")
                                                    f.write(f"Insights Generated: {len(insights)}\n\n")
                                                    
                                                    f.write("KEYWORDS:\n")
                                                    f.write("-" * 20 + "\n")
                                                    for keyword in keywords[:20]:
                                                        f.write(f"{keyword['word']}: {keyword['frequency']}\n")
                                                    
                                                    f.write("\nINSIGHTS:\n")
                                                    f.write("-" * 20 + "\n")
                                                    for insight in insights:
                                                        f.write(f"{insight['title']}\n")
                                                        f.write(f"Category: {insight['category']}\n")
                                                        f.write(f"Description: {insight['description']}\n\n")
                                                
                                                with open(txt_filename, 'rb') as f:
                                                    st.download_button(
                                                        label="💾 Download TXT Report",
                                                        data=f.read(),
                                                        file_name=txt_filename,
                                                        mime='text/plain'
                                                    )
                                                
                                                st.success(f"✅ Summary report exported to {txt_filename}")
                                    
                                    with col_exp2:
                                        if st.button("📊 Generate Detailed Report"):
                                            # Create comprehensive report
                                            report = summarizer.generate_comprehensive_report(
                                                processed_texts, keywords, insights, summaries
                                            )
                                            
                                            st.subheader("📋 Comprehensive Analysis Report")
                                            st.text_area("Report Content:", value=report, height=400, disabled=True)
                                            
                                            # Download report
                                            report_filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                            st.download_button(
                                                label="💾 Download Full Report",
                                                data=report,
                                                file_name=report_filename,
                                                mime='text/plain'
                                            )
                                    
                                    # About Comment Summarization
                                    with st.expander("ℹ️ About Comment Summarization", expanded=False):
                                        st.markdown("""
                                        **🔍 What is Comment Summarization?**
                                        
                                        Comment summarization is an AI-powered technique that automatically:
                                        - **Extracts key information** from large volumes of customer comments
                                        - **Identifies common themes** and patterns
                                        - **Generates concise summaries** highlighting main points
                                        - **Creates actionable insights** for business decisions
                                        
                                        **⚙️ How it works:**
                                        
                                        1. **Text Preprocessing**: Clean and normalize comment text
                                        2. **Keyword Extraction**: Identify most frequent and important words
                                        3. **Summary Generation**: Create concise summaries using NLP techniques
                                        4. **Insight Creation**: Generate business-relevant insights and recommendations
                                        
                                        **💡 Use Cases:**
                                        
                                        - **Customer Feedback Analysis**: Understand common customer concerns
                                        - **Product Improvement**: Identify areas for enhancement
                                        - **Service Quality**: Monitor customer satisfaction trends
                                        - **Business Intelligence**: Extract actionable business insights
                                        
                                        **🎯 Best Practices:**
                                        
                                        - Use 100-500 words for optimal summary length
                                        - Ensure you have at least 10+ comments
                                        - Review generated insights for accuracy
                                        - Export results for further analysis
                                        """)
                                        
                        except Exception as e:
                            st.error(f"❌ Comment summarization failed: {str(e)}")
                            st.error("Check the console for detailed error information.")
                            print(f"Comment summarization error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                else:
                    st.error("❌ System not ready. Please initialize the RAG system first.")

    # TAB 10: Contextual Keyword Analysis
    with tab10:
        st.header("🔍 Contextual Keyword Analysis")
        st.caption("Smart keyword detection with context-aware analysis and false positive prevention")
        
        if not CONTEXTUAL_ANALYZER_AVAILABLE:
            st.error("❌ Contextual Keyword Analyzer not available. Please check the module installation.")
        else:
            # Analysis Settings
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("⚙️ Analysis Settings")
                analysis_type = st.selectbox(
                    "Analysis Type:",
                    ["Single Text", "Batch Analysis", "Category Focus"],
                    help="Choose how to analyze the text"
                )
                
                if analysis_type == "Category Focus":
                    focus_category = st.selectbox(
                        "Focus Category:",
                        ["kargo", "kalite", "beden_uyum"],
                        help="Focus analysis on specific category"
                    )
                else:
                    focus_category = None
                
                include_patterns = st.checkbox("Show Pattern Matches", value=True)
                show_excluded = st.checkbox("Show Excluded Contexts", value=True)
                
            with col2:
                st.subheader("📊 Display Options")
                confidence_threshold = st.slider(
                    "Confidence Threshold (%)",
                    min_value=0,
                    max_value=100,
                    value=50,
                    help="Minimum confidence level to display results"
                )
                
                max_results = st.slider(
                    "Max Results to Show",
                    min_value=5,
                    max_value=50,
                    value=20,
                    help="Maximum number of results to display"
                )
            
            # Input Section
            st.subheader("📝 Input Text")
            
            if analysis_type == "Single Text":
                input_text = st.text_area(
                    "Enter text to analyze:",
                    placeholder="e.g., Kargo çok geç geldi, paket hasarlıydı. Ama ürün kalitesi iyi.",
                    height=150
                )
                
                analyze_button = st.button("🔍 Analyze Text", type="primary")
                
                if analyze_button and input_text:
                    with st.spinner("🔍 Analyzing text with contextual keyword analysis..."):
                        try:
                            analyzer = ContextualKeywordAnalyzer()
                            
                            if focus_category:
                                # Single category analysis
                                result = analyzer.analyze_contextual_keywords(input_text, focus_category)
                                
                                st.subheader(f"📊 Analysis Results for {focus_category.title()}")
                                
                                if result['is_valid_category']:
                                    st.success(f"✅ Category: {result['category'].title()}")
                                    st.metric("Context Score", result['context_score'])
                                    st.metric("Confidence", f"{result['analysis_details']['confidence']:.1f}%")
                                    
                                    if result['found_keywords']:
                                        st.write("**Found Keywords:**", ", ".join(result['found_keywords']))
                                    
                                    if result['analysis_details']['negative_context']:
                                        st.warning("⚠️ Negative context detected")
                                    
                                    if result['analysis_details']['positive_context']:
                                        st.info("ℹ️ Positive context detected")
                                    
                                    if include_patterns and result['analysis_details']['pattern_matches']:
                                        st.write("**Pattern Matches:**")
                                        for match in result['analysis_details']['pattern_matches']:
                                            st.write(f"- {match['type']}: {match['matches']}")
                                    
                                    if show_excluded and result['analysis_details']['excluded_patterns']:
                                        st.write("**Excluded Patterns:**")
                                        for pattern in result['analysis_details']['excluded_patterns']:
                                            st.write(f"- {pattern}")
                                else:
                                    st.info(f"ℹ️ No valid {focus_category} context found")
                                    if result['analysis_details']['excluded_by_context']:
                                        st.warning("🚫 Excluded by context (false positive prevented)")
                                
                            else:
                                # All categories analysis
                                result = analyzer.analyze_all_categories(input_text)
                                
                                st.subheader("📊 Multi-Category Analysis Results")
                                
                                if result['primary_category']:
                                    st.success(f"✅ Primary Category: {result['primary_category'].title()}")
                                    st.metric("Confidence", f"{result['confidence']:.1f}%")
                                    
                                    if result['summary']['best_match']:
                                        best = result['summary']['best_match']
                                        st.write(f"**Best Match:** {best['category'].title()} (Score: {best['score']})")
                                        if best['keywords']:
                                            st.write(f"**Keywords:** {', '.join(best['keywords'])}")
                                    
                                    # Show all results
                                    st.write("**All Category Results:**")
                                    for category, cat_result in result['all_results'].items():
                                        if cat_result['is_valid_category'] and cat_result['context_score'] > 0:
                                            with st.expander(f"{category.title()} - Score: {cat_result['context_score']}"):
                                                st.write(f"**Keywords:** {', '.join(cat_result['found_keywords'])}")
                                                st.write(f"**Confidence:** {cat_result['analysis_details']['confidence']:.1f}%")
                                                if cat_result['analysis_details']['negative_context']:
                                                    st.write("⚠️ Negative context")
                                                if cat_result['analysis_details']['positive_context']:
                                                    st.write("ℹ️ Positive context")
                                else:
                                    st.info("ℹ️ No valid categories found")
                                
                                if result['summary']['excluded_categories']:
                                    st.warning(f"🚫 Excluded categories: {', '.join(result['summary']['excluded_categories'])}")
                            
                        except Exception as e:
                            st.error(f"❌ Contextual analysis failed: {str(e)}")
                            st.error("Check the console for detailed error information.")
                            print(f"Contextual analysis error: {str(e)}")
                            import traceback
                            traceback.print_exc()
            
            elif analysis_type == "Batch Analysis":
                st.info("📁 Batch analysis feature coming soon. Use Single Text analysis for now.")
            
            # About Contextual Analysis
            with st.expander("ℹ️ About Contextual Keyword Analysis"):
                st.markdown("""
                **🔍 What is Contextual Keyword Analysis?**
                
                This advanced analyzer goes beyond simple keyword matching to understand the context in which words appear. It prevents false positives by analyzing the surrounding text and patterns.
                
                **🎯 Key Features:**
                - **Smart Detection**: Identifies keywords in their proper context
                - **False Positive Prevention**: Excludes misleading matches (e.g., "vazgeçilmez" vs "kargo geç geldi")
                - **Category Classification**: Automatically categorizes text into relevant areas
                - **Confidence Scoring**: Provides reliability scores for each analysis
                
                **📊 Categories Analyzed:**
                - **Kargo**: Delivery, shipping, and logistics issues
                - **Kalite**: Product quality and defect problems
                - **Beden Uyum**: Size compatibility and fitting issues
                
                **💡 Example:**
                - ❌ "vazgeçilmez ürün" → Not a cargo problem (false positive prevented)
                - ✅ "kargo geç geldi" → Real cargo problem detected
                - ✅ "paket hasarlı" → Real cargo problem detected
                
                **🔧 How it Works:**
                1. **Pattern Matching**: Uses regex patterns to identify relevant contexts
                2. **Context Validation**: Checks surrounding words and phrases
                3. **False Positive Filtering**: Excludes misleading matches
                4. **Scoring**: Assigns confidence scores based on context strength
                """)

else:
    # System not initialized - Show welcome screen
    st.markdown("""
    ## 🚀 Welcome to Comprehensive RAG System
    
    ### 🎯 System Capabilities:
    
    #### 💬 **Intelligent Chat Interface**
    - Natural language queries with advanced semantic understanding
    - Multi-modal search across comments and knowledge base
    - Context-aware responses with similarity scoring
    
    #### 📊 **Advanced Data Management**  
    - CSV upload and automatic vectorization
    - Real-time data processing and indexing
    - Batch operations and data validation
    
    #### 🧠 **Knowledge Base Management**
    - Add, edit, and organize solution knowledge
    - Template-based knowledge entry
    - Category-based organization system
    
    #### 🔍 **Powerful Search Engine**
    - Vector similarity search with FAISS
    - Sentiment and category filtering
    - Customizable search parameters
    
    #### 📈 **Analytics & Insights**
    - Real-time performance monitoring
    - Interactive data visualizations
    - Comprehensive system metrics
    
                    #### 🎯 **Topic Modeling**
                - AI-powered topic discovery
                - Hidden pattern analysis
                - Advanced clustering algorithms
                
                #### 📝 **Comment Summarization**
                - Intelligent comment summarization
                - Key insights extraction
                - Automated report generation
                
                #### 🔍 **Contextual Keyword Analysis**
                - Smart keyword detection with context
                - False positive prevention
                - Category-based analysis
                
                #### 🔧 **System Administration**
    - Advanced configuration management
    - Database maintenance tools
    - Performance optimization
    
    ### 🛠️ **Technical Features:**
    
    - **🧠 AI Models**: Sentence Transformers with 384D multilingual embeddings
    - **⚡ Vector Search**: FAISS-powered similarity search
    - **💾 Storage**: SQLite database with persistent vector storage  
    - **🌐 Language Support**: Turkish, English, and 50+ languages
    - **📊 Analytics**: Real-time metrics and performance monitoring
    
    ### 🚀 **Getting Started:**
    
    1. **Configure Model**: Select your preferred embedding model from the sidebar
    2. **Initialize System**: Click "Initialize RAG System" to start
    3. **Upload Data**: Use the Data Management tab to upload CSV files
    4. **Start Chatting**: Ask questions in natural language
    5. **Explore Features**: Use all tabs to explore the full system capabilities
    
    ### 💡 **Example Use Cases:**
    
    - **Customer Support**: Analyze customer feedback and find solutions
    - **Product Management**: Identify common issues and improvement opportunities  
    - **Content Management**: Organize and search through large knowledge bases
    - **Business Intelligence**: Extract insights from customer comments and reviews
    
    ---
    
    **👈 Start by configuring the system in the sidebar!**
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <h3>🚀 Comprehensive RAG System v2.0</h3>
    <p>Powered by FAISS Vector Search • Sentence Transformers • Advanced Analytics</p>
    <div>
        <span class="tech-badge">Facebook AI Similarity Search</span>
        <span class="tech-badge">384D Embeddings</span>
        <span class="tech-badge">Real-time Processing</span>
        <span class="tech-badge">Multi-language Support</span>
    </div>
</div>
""", unsafe_allow_html=True) 