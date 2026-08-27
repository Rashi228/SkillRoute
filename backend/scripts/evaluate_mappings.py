import os
import sys
import json
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Resource, ResourceSkill, Skill
from sqlalchemy import func

def print_metrics():
    db = SessionLocal()
    
    # 1. Total Skills and Mappings
    total_skills_mapped = db.query(func.count(func.distinct(ResourceSkill.skill_id))).scalar()
    total_mappings = db.query(func.count(ResourceSkill.resource_id)).scalar()
    
    # Mappings by source
    sources = db.query(ResourceSkill.mapping_source, func.count(ResourceSkill.resource_id)).group_by(ResourceSkill.mapping_source).all()
    
    # Averages
    avg_conf = db.query(func.avg(ResourceSkill.confidence)).scalar() or 0.0
    
    print("\n================================================")
    print("          Skill Mapping Evaluation              ")
    print("================================================")
    print(f"Unique skills mapped:        {total_skills_mapped}")
    print(f"Total mappings:              {total_mappings}")
    print(f"Average confidence:          {avg_conf:.2f}")
    print("\nMappings by Source:")
    for source, count in sources:
        s_name = source if source else "UNKNOWN"
        print(f"{s_name.ljust(25)} {count}")
    print("================================================\n")
    
if __name__ == "__main__":
    print_metrics()
