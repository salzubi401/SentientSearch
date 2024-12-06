# from src.sentientsearch.scrapers.extract_content_docling import WebContentExtractor
from src.sentientsearch.scrapers.extract_content_olostep import extract_content
from src.sentientsearch.rerankers.nvidia_reranking import get_reranking_nvidia
from src.sentientsearch.semantic_chunking import get_chunking
from markdownify import markdownify as md_to_text
import re
from readability import Document

def clean_with_markdownify(content):
    # Convert Markdown/HTML to plain text
    plain_text = md_to_text(content)

    # Post-process with regex to remove unnecessary parts:
    
    # Remove CSS imports
    plain_text = re.sub(r'@import.*?;', '', plain_text)
    
    # Remove inline images
    plain_text = re.sub(r'!\[.*?\]\(.*?\)', '', plain_text)
    
    # Remove links but keep their text
    plain_text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', plain_text)
    
    # Remove email addresses
    plain_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', plain_text)
    
    # Remove raw URLs
    plain_text = re.sub(r'https?://\S+|www\.\S+', '', plain_text)
    
    # Remove footnotes and citation references (e.g., [1], [citation needed])
    plain_text = re.sub(r'\[\d+\]', '', plain_text)
    plain_text = re.sub(r'\[citation needed\]', '', plain_text, flags=re.IGNORECASE)
    plain_text = re.sub(r'\[\w+\]', '', plain_text)  # For non-numeric footnotes like [a]

    # Remove excessive Markdown symbols
    plain_text = re.sub(r'(#+\s?|={2,}|-{2,})', '', plain_text)
    
    # Clean up excessive whitespace and newlines
    plain_text = re.sub(r'\s{2,}', ' ', plain_text)
    plain_text = re.sub(r'\n\s*\n', '\n', plain_text).strip()

    return plain_text


def populate_sources(sources, num_elements, query):
    try:
        # Filter valid sources and get their links
        valid_sources = [(i, source) for i, source in enumerate(sources[:num_elements]) if source]
        if not valid_sources:
            return sources
            
        # Extract all content at once
        # doc_converter = WebContentExtractor()
        links = [source['link'] for _, source in valid_sources]
        # html_contents = doc_converter.extract_website_content(links)
        uncleaned_contents = [Document(x['html_content']) for x in extract_content(links)]
        html_contents = [clean_with_markdownify(x.summary()) for x in uncleaned_contents]
        # Update sources with their HTML content
        for (i, source), html in zip(valid_sources, html_contents):
            final_content = ""
            if html:
                #TODO: Chunking is sometimes failing, it's either due to token length being too high because of weird characters
                try:    
                    chunked_content = get_chunking(html)
                    reranked_content = get_reranking_nvidia(chunked_content, query, 5)
                    final_content = "\n\n".join(reranked_content)
                except Exception as e:
                    print(f"Error in reranking: {e}")
                    pass
            source['html'] = final_content
            sources[i] = source

    except Exception as e:
        print(f"Error in populate_sources: {e}")
        
    return sources