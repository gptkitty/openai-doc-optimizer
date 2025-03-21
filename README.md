# OpenAI Deep Research Document Optimizer

A specialized tool to optimize deep research documents created by OpenAI for Retrieval-Augmented Generation (RAG) systems by improving token efficiency while preserving source information.

## Features

- Extracts URLs from Markdown links and replaces them with numbered citations
- Creates a references section at the end of the document
- Groups references by domain for better organization (optional)
- Maintains domain names in citations for better context (optional)
- Handles both inline Markdown links and raw URLs
- Streamlit UI for easy document processing with token and file size metrics
- Command-line interface for batch processing

## Why Use This Optimizer?

OpenAI deep research documents contain valuable information but often include numerous links that consume tokens in RAG systems. This specialized tool helps you:

1. **Reduce Token Consumption**: By converting long URLs to short numeric references
2. **Preserve Source Information**: All URLs are maintained in an organized references section
3. **Improve Readability**: Clean citations make documents easier to read
4. **Maintain Context**: Domain grouping helps maintain the context of references

## Installation

```bash
# Clone the repository
git clone https://github.com/gptkitty/openai-doc-optimizer.git
cd openai-doc-optimizer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Basic usage
python rag_optimizer.py input.md output.md

# Disable domain grouping
python rag_optimizer.py input.md output.md --no-group-domains

# Disable domain name preservation in citations
python rag_optimizer.py input.md output.md --no-keep-domains

# Disable both features
python rag_optimizer.py input.md output.md --no-group-domains --no-keep-domains
```

### Streamlit Web Interface

```bash
streamlit run app.py
```

Then open your browser to http://localhost:8501

## Example

### Before Optimization

```markdown
Check out this [interesting article](https://example.com/article/123) about RAG systems.
There's also more information at https://another-site.com/info.
```

### After Optimization

```markdown
Check out this interesting article[1] about RAG systems.
There's also more information at [2].

## References

### example.com

[1] https://example.com/article/123

### another-site.com

[2] https://another-site.com/info
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the need to optimize OpenAI research documents for RAG systems
- Thanks to the open-source community for various tools and libraries used in this project

## Author

Created by Carlos Chavarria (hello@productcarlos.com)