import asyncio
import aiohttp
from typing import List
from .base import NormalizedResource

class URLValidator:
    def __init__(self, concurrency: int = 10, timeout: int = 10, max_retries: int = 2):
        self.concurrency = concurrency
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _validate_url(self, session: aiohttp.ClientSession, resource: NormalizedResource):
        async with self.semaphore:
            url = resource.url
            if not url:
                resource.verification_status = "FAILED"
                resource.validation_error = "Missing URL"
                return

            for attempt in range(self.max_retries):
                try:
                    # Use a user agent to avoid basic blocks
                    headers = {"User-Agent": "SkillRoute-Validator/1.0"}
                    async with session.get(url, timeout=self.timeout, headers=headers, allow_redirects=True) as response:
                        resource.http_status = response.status
                        resource.final_url = str(response.url)
                        
                        if response.status == 200:
                            resource.verification_status = "VERIFIED"
                            return
                        elif response.status in [404, 410]:
                            resource.verification_status = "FAILED"
                            resource.validation_error = f"HTTP {response.status}"
                            return
                        else:
                            resource.verification_status = "UNKNOWN"
                            resource.validation_error = f"HTTP {response.status}"
                            return
                except asyncio.TimeoutError:
                    if attempt == self.max_retries - 1:
                        resource.verification_status = "UNKNOWN"
                        resource.validation_error = "Timeout"
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        resource.verification_status = "FAILED"
                        resource.validation_error = str(e)
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

    async def validate_batch(self, resources: List[NormalizedResource]):
        """Validates a batch of resources concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._validate_url(session, r) for r in resources]
            await asyncio.gather(*tasks)

def validate_resources_sync(resources: List[NormalizedResource], concurrency=10):
    """Entry point to run the async validation synchronously from the pipeline."""
    validator = URLValidator(concurrency=concurrency)
    asyncio.run(validator.validate_batch(resources))
