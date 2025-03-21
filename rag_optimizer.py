import re
import sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

def process_markdown_file(input_file, output_file, group_by_domain=True, keep_domain_names=True):
    """
    Process a Markdown file to optimize it for RAG systems.
    
    Args:
        input_file (str): Path to the input Markdown file
        output_file (str): Path to save the optimized output file
        group_by_domain (bool): Whether to group references by domain
        keep_domain_names (bool): Whether to keep domain names in citations
        
    Returns:
        int: Number of unique URLs processed
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize URL collection and counter
    urls = []
    url_map = {}
    domain_groups = defaultdict(list) if group_by_domain else None
    current_url_index = 1
    
    # Regular expression to find Markdown links with URLs and citation-style links
    # Matches [text](url) patterns and domain[citation] patterns
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    citation_pattern = r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\[(\d+)\]'
    
    # Function to replace each URL with a citation number
    def replace_url(match):
        nonlocal current_url_index
        text, url = match.groups()
        
        # Clean up the URL if it has any extra markers
        url = url.split('#')[0]  # Remove any anchors
        
        # If we haven't seen this URL before, add it to our collection
        if url not in url_map:
            url_map[url] = current_url_index
            urls.append(url)
            
            if group_by_domain:
                domain = urlparse(url).netloc
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append((current_url_index, url))
                
            current_url_index += 1
        
        # Replace with citation number
        return f"{text}[{url_map[url]}]"
    
    # Replace domain[citation] patterns if needed
    if not keep_domain_names:
        def replace_citation(match):
            domain, citation_num = match.groups()
            # We're not actually using the citation number, just removing the domain
            return f"[{citation_num}]"
        
        content = re.sub(citation_pattern, replace_citation, content)
    
    # Replace all Markdown links with citation numbers
    content = re.sub(link_pattern, replace_url, content)
    
    # Also find and replace any raw URLs
    raw_url_pattern = r'(?<!\()(https?://[^\s]+)(?!\))'
    
    def replace_raw_url(match):
        nonlocal current_url_index
        url = match.group(1)
        
        # Clean up the URL if it has any extra markers
        url = url.split('#')[0]  # Remove any anchors
        
        # If we haven't seen this URL before, add it to our collection
        if url not in url_map:
            url_map[url] = current_url_index
            urls.append(url)
            
            if group_by_domain:
                domain = urlparse(url).netloc
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append((current_url_index, url))
                
            current_url_index += 1
        
        # Replace with citation number
        return f"[{url_map[url]}]"
    
    content = re.sub(raw_url_pattern, replace_raw_url, content)
    
    # Add references section at the end
    content += "\n\n## References\n\n"
    
    if group_by_domain:
        # Group references by domain
        for domain, urls_in_domain in domain_groups.items():
            content += f"### {domain}\n\n"
            for idx, url in urls_in_domain:
                content += f"[{idx}] {url}\n\n"
    else:
        # Simple list of references
        for i, url in enumerate(urls, 1):
            content += f"[{i}] {url}\n\n"
    
    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(urls)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Markdown files to optimize for RAG systems')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('output', help='Output Markdown file')
    parser.add_argument('--no-group-domains', action='store_false', dest='group_domains', 
                        help='Do not group references by domain')
    parser.add_argument('--no-keep-domains', action='store_false', dest='keep_domains', 
                        help='Do not keep domain names in citations')
    
    # Set the defaults here
    parser.set_defaults(group_domains=True, keep_domains=True)
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    
    num_urls = process_markdown_file(args.input, args.output, args.group_domains, args.keep_domains)
    print(f"Processed {num_urls} unique URLs and saved to {args.output}")