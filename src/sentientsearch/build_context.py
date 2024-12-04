import logging
import time
from src.sentientsearch.rerankers.nvidia_reranking import get_reranking_nvidia
from src.sentientsearch.semantic_chunking import get_chunking

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""

Idea: 
This might need to be changed a little bit,
We need to chunk the html content, and then retrieve chunks from the HTML
Then we need to rerank the chunks

"""
def build_context(sources_result, query, pro_mode, date_context):
    """
      Build context from search results.

      :param sources_result: Dictionary containing search results
      :param query: Search query string
      :param pro_mode: Boolean indicating whether to use pro mode (reranking)
      :param date_context: Date context string
      :return: Built context as a string
      """
    try:
        combined_list = []

        organic_results = sources_result.get('organic', [])
        graph = sources_result.get('graph')
        answer_box = sources_result.get('answerBox')

        snippets = [
            f"{item['snippet']} {item.get('date', '')}"
            for item in organic_results if 'snippet' in item  # Ensure there's always a snippet
        ]

        combined_list.extend(snippets)

        html_text = " ".join(item['html'] for item in organic_results if 'html' in item)
        #TODO: Need to dig into this chunking part, especially if we're doing pro mode...
        if html_text is not None and len(html_text) > 200:
            start_time = time.time()
            chunks = get_chunking(html_text)
            chunking_time = time.time() - start_time
            logger.info(f"Chunking took {chunking_time:.2f} seconds")
            combined_list.extend(chunks)

        # Extract top stories titles
        if sources_result.get('topStories') is not None:
            top_stories_titles = [item['title'] for item in sources_result.get('topStories') if 'title' in item]
            combined_list.extend(top_stories_titles)

        # Add descriptions and answers from 'graph' and 'answerBox'
        if graph is not None:
            graph_desc = graph.get('description')
            if graph_desc:
                combined_list.append(graph_desc)

        if answer_box is not None:
            for key in ['answer', 'snippet']:
                if key in answer_box:  # Use this if you want to append regardless of the value (including None)
                    combined_list.append(answer_box[key])

        if pro_mode:
            start_time = time.time()
            final_list = get_reranking_nvidia(combined_list, query + date_context, 15)

            reranking_time = time.time() - start_time
            logger.info(f"Reranking took {reranking_time:.2f} seconds")
        else:
            final_list = combined_list

        search_contexts = "\n\n".join(final_list)
        return search_contexts
    except Exception as e:
        logger.exception(f"An error occurred while building context: {e}")
        return ""