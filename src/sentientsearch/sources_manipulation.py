from src.sentientsearch.scrapers.extract_content_docling import WebContentExtractor


def populate_sources(sources, num_elements):
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
            source['html'] = html
            sources[i] = source
            
    except Exception as e:
        print(f"Error in populate_sources: {e}")
        
    return sources
 