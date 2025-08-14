#!/usr/bin/env python3
"""
Script to fix plotly usage in comprehensive_rag_streamlit.py
Makes all plotly usage conditional based on PLOTLY_AVAILABLE flag
"""

import re

def fix_plotly_usage():
    with open('comprehensive_rag_streamlit.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find plotly chart creation and usage
    patterns = [
        # Find px.bar, px.pie, px.line, go.Figure usage
        (r'(\s+)(fig_\w+\s*=\s*px\.\w+\([^)]*\)\s*\n(?:\s+[^\n]*\n)*\s+st\.plotly_chart\(fig_\w+[^)]*\))', 
         r'\1if PLOTLY_AVAILABLE:\n\1    \2\n\1else:\n\1    st.info("📊 Chart visualization disabled (Plotly not available)")'),
        
        # Find st.plotly_chart usage
        (r'(\s+)(st\.plotly_chart\([^)]*\))', 
         r'\1if PLOTLY_AVAILABLE:\n\1    \2\n\1else:\n\1    st.info("📊 Chart visualization disabled (Plotly not available)")'),
    ]
    
    # Apply patterns
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write back
    with open('comprehensive_rag_streamlit.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Plotly usage has been made conditional!")

if __name__ == "__main__":
    fix_plotly_usage()
