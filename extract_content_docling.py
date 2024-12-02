from docling.document_converter import DocumentConverter

class WebContentExtractor:
    def __init__(self):
        """Initialize the WebContentExtractor with a DocumentConverter instance."""
        self.converter = DocumentConverter()

    def extract_website_content(self, urls):
        """
        Extracts and cleans the main content from one or more website URLs.

        Args:
        urls (str or list): Single URL string or list of URL strings to extract content from.

        Returns:
        str or list: If single URL, returns cleaned content string.
                     If list of URLs, returns list of cleaned content strings.
        """
        try:
            print("Converting URLs:", urls if isinstance(urls, str) else len(urls), "URLs")
            
            # Handle single URL
            if isinstance(urls, str):
                loader = self.converter.convert(urls)
                data = [x[0].orig for x in loader.document.iterate_items() if x[0].label.value == 'paragraph']
                data = [x.replace("\n", "") for x in data]
                clean_text = "\n\n".join(data)
                return clean_text[:4000] if len(clean_text) > 200 else ""
            
            # Handle list of URLs
            loaders = self.converter.convert_all(urls)
            results = []
            for loader in loaders:
                data = [x[0].orig for x in loader.document.iterate_items() if x[0].label.value == 'paragraph']
                data = [x.replace("\n", "") for x in data]
                clean_text = "\n\n".join(data)
                results.append(clean_text[:4000] if len(clean_text) > 200 else "")
            
            return results

        except Exception as error:
            print('Error extracting main content:', error)
            return "" if isinstance(urls, str) else [""] * len(urls)

    def __del__(self):
        """Cleanup method to properly close the converter."""
        try:
            self.converter.close()
        except:
            pass
