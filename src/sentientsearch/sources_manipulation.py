from src.sentientsearch.scrapers.extract_content_docling import WebContentExtractor
from src.sentientsearch.rerankers.nvidia_reranking import get_reranking_nvidia
from src.sentientsearch.semantic_chunking import get_chunking

def populate_sources(sources, num_elements, query):
    try:
        # Filter valid sources and get their links
        valid_sources = [(i, source) for i, source in enumerate(sources[:num_elements]) if source]
        if not valid_sources:
            return sources
            
        # Extract all content at once
        doc_converter = WebContentExtractor()
        links = [source['link'] for _, source in valid_sources]
        html_contents = doc_converter.extract_website_content(links)
        # Update sources with their HTML content
        for (i, source), html in zip(valid_sources, html_contents):
            final_content = ""
            if html:
                chunked_content = get_chunking(html)
                #Grab the top 5 results, I don't think we need more than 5 passages related to query...
                reranked_content = get_reranking_nvidia(chunked_content, query, 5)
                final_content = "\n\n".join(reranked_content)
            source['html'] = final_content
            sources[i] = source

    except Exception as e:
        print(f"Error in populate_sources: {e}")
        
    return sources
 