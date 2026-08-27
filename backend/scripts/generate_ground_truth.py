import sys
import os
import json
import re
from typing import List, Dict

sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from models import Resource, Skill

def main():
    db = SessionLocal()
    
    # Get 100 random resources
    resources = db.query(Resource).filter(Resource.dataset_name == 'coursera .csv').order_by(Resource.id).limit(100).all()
    skills = db.query(Skill).all()
    
    results = []
    out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "llm_assisted_ground_truth.json")
    
    print(f"Generating heuristic ground truth for {len(resources)} resources...")
    for i, res in enumerate(resources):
        text = f"{res.title} {res.description}".lower()
        expected = []
        
        for skill in skills:
            # Check name
            if re.search(r'\b' + re.escape(skill.name.lower()) + r'\b', text):
                expected.append(skill.id)
                continue
                
            # Check aliases
            if skill.aliases:
                try:
                    aliases = json.loads(skill.aliases)
                    for alias in aliases:
                        if re.search(r'\b' + re.escape(alias.lower()) + r'\b', text):
                            expected.append(skill.id)
                            break
                except:
                    pass
                    
        results.append({
            "resource_id": res.id,
            "resource_title": res.title,
            "expected_skill_ids": expected,
            "review_status": "UNVERIFIED_HEURISTIC",
            "reviewer_notes": "Generated via strict keyword heuristic"
        })
        print(f"[{i+1}/100] Mapped Resource ID {res.id} -> {expected}")
            
    with open(out_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved ground truth to {out_file}")

if __name__ == "__main__":
    main()
