import os
import sys
import time
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator

async def test_youtube():
    db = SessionLocal()
    
    print("\n--- TEST 4: YOUTUBE DISCOVERY ---", flush=True)
    
    for i in range(1, 4):
        print(f"\n[Request {i}] Instantiating Orchestrator...", flush=True)
        start = time.time()
        orchestrator = YouTubeDiscoveryOrchestrator(db)
        print(f"[Request {i}] Calling discover()...", flush=True)
        
        try:
            res = await orchestrator.discover(
                skill_id=1,  # Assuming ID 1 exists (Python/RAG)
                learner_level="INTERMEDIATE",
                goal="General learning",
                constraints={},
                is_struggling=False
            )
            elapsed = time.time() - start
            print(f"[Request {i}] Discovery SUCCESS in {elapsed:.2f}s", flush=True)
            print(f"[Request {i}] Resources returned: {len(res.get('resources', []))}", flush=True)
            
            # Check if Match % exists
            if res.get('resources'):
                score = res['resources'][0].get('metrics', {}).get('final_score')
                print(f"[Request {i}] Top Resource Final Score (Match %): {score}", flush=True)
        except Exception as e:
            print(f"[Request {i}] FAILED: {str(e)}", flush=True)
            
    db.close()

if __name__ == "__main__":
    asyncio.run(test_youtube())
