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
    page_title="OpenAI Document Optimizer",
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
st.subheader("Optimize OpenAI deep research documents for RAG systems")

with st.expander("About this tool", expanded=True):
    st.markdown("""
    This specialized tool optimizes OpenAI research documents for Retrieval-Augmented Generation (RAG) systems by:
    
    - Extracting URLs and replacing them with numbered citations
    - Creating a references section at the end of the document
    - Grouping references by domain (optional)
    - Maintaining domain names in citations (optional)
    - NOTE: This is not a general markdown optimizer! Non-deep research documents may result in an increase in tokens
    
    The result is a more token-efficient document that preserves all source information, typically reducing token usage by ~20%.
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
    
    # Process button
    if st.button("Process Files"):
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
                
                # Display results in the container
                with results_container:
                    st.subheader(f"Results for {uploaded_file.name}")
                    
                    # Side-by-side comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Original Document")
                        st.text_area("", original_content, height=300)
                        st.info(f"Size: {original_size} bytes | Tokens: {original_tokens}")
                    
                    with col2:
                        st.markdown("### Optimized Document")
                        st.text_area("", processed_content, height=300)
                        st.info(f"Size: {processed_size} bytes | Tokens: {processed_tokens}")
                    
                    # Token savings
                    token_diff = original_tokens - processed_tokens
                    token_percent = (token_diff / original_tokens * 100) if original_tokens > 0 else 0
                    
                    if token_diff > 0:
                        st.success(f"Saved {token_diff} tokens ({token_percent:.1f}% reduction)")
                    elif token_diff < 0:
                        st.warning(f"Increased by {abs(token_diff)} tokens ({abs(token_percent):.1f}% increase)")
                    else:
                        st.info("No change in token count")
                    
                    # Download button for processed file
                    st.download_button(
                        label="Download Optimized File",
                        data=processed_content.encode('utf-8'),
                        file_name=f"optimized_{uploaded_file.name}",
                        mime="text/markdown"
                    )
                    
                    st.markdown("---")
                
                # Clean up temp files
                os.unlink(input_path)
                os.unlink(output_path)

else:
    st.info("Please upload one or more Markdown files to begin")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Carlos Chavarria | [GitHub Repository](https://github.com/gptkitty/openai-doc-optimizer)")