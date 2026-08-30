import os
import sys
import asyncio
import time
from sqlalchemy import func
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill, Resource, ResourceSkill
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator
from services.youtube.youtube_cache import YouTubeCache

# 20+ High value demo skills
TARGET_SKILLS = [
    "Python",
    "JavaScript",
    "React",
    "Node.js",
    "Backend Development",
    "Frontend Development",
    "Full Stack Developer",
    "FastAPI",
    "SQL",
    "Data Structures",
    "Algorithms",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Generative AI",
    "Large Language Models",
    "RAG",
    "Docker",
    "Kubernetes",
    "DevOps",
    "Cloud Computing",
    "Amazon Web Services",
    "Data Engineering",
    "Cybersecurity"
]

async def warm_cache():
    db = SessionLocal()
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    cache = YouTubeCache(db)
    
    found_skills = []
    missing_skills = []
    
    print("==================================================")
    print("1. RESOLVING SKILLS")
    print("==================================================")
    
    # Resolve skill IDs by name
    for s_name in TARGET_SKILLS:
        skill = db.query(Skill).filter(func.lower(Skill.name) == s_name.lower()).first()
        if skill:
            found_skills.append(skill)
        else:
            missing_skills.append(s_name)
            
    print("\nFOUND:")
    for s in found_skills:
        print(f"{s.name} -> {s.id}")
        
    print("\nMISSING:")
    for m in missing_skills:
        print(m)
        
    print("\n==================================================")
    print("2. WARMING CACHE (YOUTUBE_DISCOVERY)")
    print("==================================================")
    
    skipped = 0
    warmed = 0
    total_new_resources = 0
    youtube_api_calls = 0
    groq_api_calls = 0
    
    for skill in found_skills:
        is_hit, cached = cache.check_cache(skill.id, is_struggling=False)
        
        if is_hit:
            print(f"[SKIP] {skill.name} — {len(cached)} cached resources")
            skipped += 1
            continue
            
        print(f"[WARM] {skill.name} — {len(cached)} cached -> discovering...")
        
        try:
            # Discover internally tracks API calls in its own metrics, but we can capture the delta
            res = await orchestrator.discover(skill.id, "INTERMEDIATE", "Goal", {})
            
            status = res.get('status')
            metrics = res.get('metrics', {})
            
            y_calls = metrics.get('youtube_api_calls', 0)
            g_calls = metrics.get('groq_calls', 0)
            
            youtube_api_calls += y_calls
            groq_api_calls += g_calls
            
            if status in ['SUCCESS', 'DISCOVERED']:
                _, new_cached = cache.check_cache(skill.id, is_struggling=False)
                print(f"[WARMED] {skill.name} — {len(new_cached)} verified resources (YouTube calls: {y_calls}, Groq calls: {g_calls})")
                warmed += 1
                total_new_resources += len(new_cached)
            else:
                print(f"[FAILED] {skill.name} — Status: {status}, Message: {res.get('message')}")
        except Exception as e:
            print(f"[ERROR] {skill.name} — Failed with exception: {e}")
            
    print("\n==================================================")
    print("3. VERIFICATION REPORT")
    print("==================================================")
    
    print(f"{'Skill':<25} | {'Cached':<8} | {'Verified':<8} | {'Mapping Source'}")
    print("-" * 70)
    
    for skill in found_skills:
        _, cached = cache.check_cache(skill.id, is_struggling=False)
        print(f"{skill.name:<25} | {len(cached):<8} | {len(cached):<8} | YOUTUBE_DISCOVERY")
        
    print("\n==================================================")
    print("4. LATENCY TEST")
    print("==================================================")
    
    test_skills = ["RAG", "React", "Python", "Docker", "Generative AI"]
    for ts in test_skills:
        skill = db.query(Skill).filter(func.lower(Skill.name) == ts.lower()).first()
        if not skill:
            print(f"[LATENCY] {ts} - SKIPPED (Not found in DB)")
            continue
            
        start_time = time.time()
        res = await orchestrator.discover(skill.id, "INTERMEDIATE", "Goal", {})
        latency = time.time() - start_time
        
        metrics = res.get('metrics', {})
        print(f"[LATENCY] {ts}: {latency:.3f}s | Cache Hit: {res.get('status') == 'CACHE_HIT'} | YT Calls: {metrics.get('youtube_api_calls', 0)} | Groq: {metrics.get('groq_calls', 0)}")
        
    print("\n==================================================")
    print("SUMMARY")
    print("==================================================")
    print(f"Skills Found:       {len(found_skills)}")
    print(f"Skills Missing:     {len(missing_skills)}")
    print(f"Skills Skipped:     {skipped}")
    print(f"Skills Warmed:      {warmed}")
    print(f"New Resources:      {total_new_resources}")
    print(f"YouTube API Calls:  {youtube_api_calls}")
    print(f"Groq API Calls:     {groq_api_calls}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(warm_cache())
