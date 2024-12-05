import orjson as json
from dotenv import load_dotenv

load_dotenv()

from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.sentientsearch.llms.fireworks_api import get_answer as get_answer_fireworks, get_relevant_questions as get_relevant_questions_fireworks
from src.sentientsearch.sources_searcher import get_sources
from src.sentientsearch.build_context import build_context
from src.sentientsearch.sources_manipulation import populate_sources


app = FastAPI()

# allow_origins=["https://openperplex.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Allow all methods or specify like ["POST", "GET"]
    allow_headers=["*"],  # Allow all headers or specify
)

load_dotenv()

class TimeoutException(Exception):
    pass


@app.get("/")
def root():
    return {"message": "hello world openperplex v1"}


@app.get("/up_test")
def up_test():
    # test for kamal deploy
    return {"status": "ok"}

#TODO: experimental add timeout
import multiprocessing

def populate_sources_global_wrapper(args):
    """
    Wrapper function to call the actual populate_sources with unpacked arguments.
    """
    organic_sources, num_sources, query = args
    return populate_sources(organic_sources, num_sources, query)

def populate_sources_with_timeout(organic_sources, num_sources, query, timeout=30):
    """
    Run populate_sources in a subprocess with a timeout.
    """
    with multiprocessing.Pool(processes=1) as pool:
        # Pass arguments as a tuple since multiprocessing needs a single argument
        result = pool.apply_async(populate_sources_global_wrapper, ((organic_sources, num_sources, query),))
        try:
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            print(f"Timeout occurred in populate_sources for {timeout} seconds")
            pool.terminate()  # Kill the subprocess
            return organic_sources
        except Exception as e:
            print(f"Error in populate_sources: {e}")
            return organic_sources


# you can change to post if typical your query is too long
@app.get("/search")
def ask(query: str, date_context: str, stored_location: str, pro_mode: bool = True):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    def generate():
        try:
            #This only deals with serperAPI and organizes the outputs in a dictionary
            #Overall seems good, no need to mess with this...

            sources_result = get_sources(query, pro_mode, stored_location)
            yield "data:" + json.dumps({'type': 'sources', 'data': sources_result}).decode() + "\n\n"

            #Essentially, if we're in pro mode, then we're extracting content from 2 websites using langchain
            #TODO: Figure out number of websites (I'm guessing 1-3 is good); use docling?
            if sources_result.get('organic') is not None and pro_mode is True:
                # set the number of websites to scrape : here = 2
                sources_result['organic'] = populate_sources_with_timeout(
                    sources_result['organic'], num_sources=4, query=query, timeout=30
                )


            search_contexts = build_context(sources_result, query, pro_mode, date_context)
            # for chunk in get_answer(query, search_contexts, date_context):
            for chunk in get_answer_fireworks(query, search_contexts, date_context):
                yield "data:" + json.dumps({'type': 'llm', 'text': chunk}).decode() + "\n\n"

        except Exception as e:
            print(e)
            yield "data:" + json.dumps(
                {'type': 'error',
                 'data': "We are currently experiencing some issues. Please try again later."}).decode() + "\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
