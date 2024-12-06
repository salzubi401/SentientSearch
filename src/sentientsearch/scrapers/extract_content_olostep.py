import asyncio
import aiohttp
from typing import Union, List
from dotenv import load_dotenv
import os
import nest_asyncio
nest_asyncio.apply()
# Load environment variables from .env file
load_dotenv()

# Retrieve the OLOSTEP_API_KEY from environment variables
OLOSTEP_API_KEY = os.getenv('OLOSTEP_API_KEY')

async def scrape_url(session: aiohttp.ClientSession, url: str, olo_api_key: str):
    endpoint = "https://agent.olostep.com/olostep-p2p-incomingAPI"
    params = {
        "token": olo_api_key,
        "url": url,
        "timeout": 65,
        "waitBeforeScraping": 0,
        "removeCSSselectors": 'default',
        "removeImages": "true",
        "nodeCountry": "US",
        "expandHtml": "true"
    }
    
    try:
        async with session.get(endpoint, params=params) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

async def scrape_urls(urls: Union[str, List[str]], olo_api_key: str = OLOSTEP_API_KEY):
    if isinstance(urls, str):
        urls = [urls]
    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url(session, url, olo_api_key) for url in urls]
        return await asyncio.gather(*tasks)

def extract_content(urls: Union[str, List[str]], olo_api_key: str = OLOSTEP_API_KEY):
    return asyncio.run(scrape_urls(urls, olo_api_key))
