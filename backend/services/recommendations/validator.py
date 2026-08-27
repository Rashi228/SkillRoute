import asyncio
import aiohttp
from typing import List, Dict, Any

async def validate_urls(urls: List[str]) -> Dict[str, bool]:
    results = {}
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                # Use GET for more reliable responses than HEAD on some docs sites
                async with session.get(url, timeout=5) as response:
                    results[url] = response.status == 200
            except:
                results[url] = False
    return results

async def filter_valid_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not resources:
        return []
    
    urls = [r["url"] for r in resources if "url" in r]
    if not urls:
        return resources
        
    validation_results = await validate_urls(urls)
    
    valid_resources = []
    for r in resources:
        if "url" in r:
            if validation_results.get(r["url"], False):
                valid_resources.append(r)
        else:
            valid_resources.append(r)
            
    return valid_resources
