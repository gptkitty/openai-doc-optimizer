import streamlit as st
import re
import sys
import os
import tempfile
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
import tiktoken

# Import the core functionality from the main script
from rag_optimizer import process_markdown_file

# Set page configuration
st.set_page_config(
    page_title="Deep Research Document Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to count tokens using tiktoken
def count_tokens(text, model="gpt-4"):
    """Count the number of tokens in a text string"""
    try:
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))
    except:
        # Fallback to cl100k_base encoding if model-specific encoding is not found
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))

# Main app layout
st.title("Deep Research Document Optimizer")
st.subheader("Optimize deep research documents for RAG systems")

with st.expander("About this tool", expanded=True):
    st.markdown("""
    This specialized tool optimizes OpenAI deep research documents for Retrieval-Augmented Generation (RAG) systems by:
    
    - Extracting URLs and replacing them with numbered citations
    - Creating a references section at the end of the document
    - Grouping references by domain (optional)
    - Maintaining domain names in citations (optional)
    - **Note**: This is not a general markdown optimizer! Non-deep research documents may result in an increase in tokens
    - **Privacy Notice**: Your data is processed entirely in-memory and is cleared when the app restarts, your session ends, or you close the browser tab. No document content is stored or retained after processing.
    """)

# Sidebar options
st.sidebar.header("Configuration")
group_domains = st.sidebar.checkbox("Group references by domain", value=True)
keep_domains = st.sidebar.checkbox("Keep domain names in citations", value=True)
model_option = st.sidebar.selectbox(
    "Token counting model",
    options=["gpt-3.5-turbo", "gpt-4", "claude-3", "llama-3"],
    index=1
)

# File upload section
st.header("Upload Markdown Files")
uploaded_files = st.file_uploader("Choose Markdown files", type=["md", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
    
    # Create a container for the file processing results
    results_container = st.container()
    
    # Store processed results in session state to persist across reruns
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = []

    # Process button
    if st.button("Process Files") or (hasattr(st.session_state, 'processed_results') and st.session_state.processed_results):
        if st.button("Process Files"):
            # Clear previous results when processing new files
            st.session_state.processed_results = []
            
            with st.spinner("Processing files..."):
                for uploaded_file in uploaded_files:
                    # Create temp files for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_input:
                        temp_input.write(uploaded_file.getvalue())
                        input_path = temp_input.name
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_output:
                        output_path = temp_output.name
                    
                    # Process the file
                    process_markdown_file(input_path, output_path, group_domains, keep_domains)
                    
                    # Read the processed file
                    with open(output_path, 'r', encoding='utf-8') as f:
                        processed_content = f.read()
                    
                    # Calculate stats
                    original_content = uploaded_file.getvalue().decode('utf-8')
                    original_size = len(original_content.encode('utf-8'))
                    processed_size = len(processed_content.encode('utf-8'))
                    original_tokens = count_tokens(original_content, model_option)
                    processed_tokens = count_tokens(processed_content, model_option)
                    
                    # Store results in session state
                    st.session_state.processed_results.append({
                        'file_name': uploaded_file.name,
                        'original_content': original_content,
                        'processed_content': processed_content,
                        'original_size': original_size,
                        'processed_size': processed_size,
                        'original_tokens': original_tokens,
                        'processed_tokens': processed_tokens
                    })
                    
                    # Clean up temp files
                    os.unlink(input_path)
                    os.unlink(output_path)
        
        # Display all results from session state
        with results_container:
            for result in st.session_state.processed_results:
                st.subheader(f"Results for {result['file_name']}")
                
                # Side-by-side comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Original Document")
                    st.text_area("", result['original_content'], height=300, key=f"orig_{result['file_name']}")
                    st.info(f"Size: {result['original_size']} bytes | Tokens: {result['original_tokens']}")
                
                with col2:
                    st.markdown("### Optimized Document")
                    st.text_area("", result['processed_content'], height=300, key=f"proc_{result['file_name']}")
                    st.info(f"Size: {result['processed_size']} bytes | Tokens: {result['processed_tokens']}")
                
                # Token savings
                token_diff = result['original_tokens'] - result['processed_tokens']
                token_percent = (token_diff / result['original_tokens'] * 100) if result['original_tokens'] > 0 else 0
                
                if token_diff > 0:
                    st.success(f"Saved {token_diff} tokens ({token_percent:.1f}% reduction)")
                elif token_diff < 0:
                    st.warning(f"Increased by {abs(token_diff)} tokens ({abs(token_percent):.1f}% increase)")
                else:
                    st.info("No change in token count")
                
                # Download button for processed file
                st.download_button(
                    label="Download Optimized File",
                    data=result['processed_content'].encode('utf-8'),
                    file_name=f"optimized_{result['file_name']}",
                    mime="text/markdown",
                    key=f"download_{result['file_name']}"
                )
                
                st.markdown("---")

else:
    st.info("Please upload one or more Markdown files to begin")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Carlos Chavarria | [GitHub Repository](https://github.com/gptkitty/openai-doc-optimizer)")