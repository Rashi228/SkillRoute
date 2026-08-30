import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from database import SessionLocal
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from services.skill_mapping.semantic_matcher import SemanticMatcher, _MODEL_INIT_COUNT

def instantiate_matcher(worker_id):
    db = SessionLocal()
    store = SkillEmbeddingStore(db)
    print(f"[Worker {worker_id}] Instantiating SemanticMatcher...", flush=True)
    start = time.time()
    matcher = SemanticMatcher(store)
    elapsed = time.time() - start
    print(f"[Worker {worker_id}] Instantiated SemanticMatcher in {elapsed:.2f}s", flush=True)
    db.close()

def test_singleton():
    print("\n--- TEST 1: SEQUENTIAL REQUESTS ---")
    instantiate_matcher(1)
    instantiate_matcher(2)
    instantiate_matcher(3)
    
    print(f"Init count after sequential: {_MODEL_INIT_COUNT}")
    
    print("\n--- TEST 2: CONCURRENT REQUESTS ---")
    threads = []
    for i in range(4, 9):
        t = threading.Thread(target=instantiate_matcher, args=(i,))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
        
    print(f"Init count after concurrent: {_MODEL_INIT_COUNT}")

if __name__ == "__main__":
    test_singleton()
