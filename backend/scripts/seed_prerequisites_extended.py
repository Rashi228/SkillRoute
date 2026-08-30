import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill, SkillPrerequisite

def detect_cycles(graph):
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path + [neighbor]):
                    return True
            elif neighbor in rec_stack:
                print(f"CYCLE DETECTED: {' -> '.join(str(n) for n in path + [neighbor])}")
                return True
                
        rec_stack.remove(node)
        return False
        
    for node in list(graph.keys()):
        if node not in visited:
            if dfs(node, [node]):
                return True
    return False

def seed_prerequisites():
    db = SessionLocal()
    
    # 1. Fetch all skills
    skills = {s.name: s.id for s in db.query(Skill).all()}
    
    if "Programming Fundamentals" not in skills:
        print("Error: Run seed_skills_demo.py first.")
        return
        
    # 2. Define new logically meaningful prerequisites
    # format: (prerequisite_name, target_name)
    new_edges = [
        # Foundation
        ("Programming Fundamentals", "Python"),
        ("Programming Fundamentals", "JavaScript"),
        ("Programming Fundamentals", "Java"),
        ("Programming Fundamentals", "C++"),
        ("Programming Fundamentals", "Go"),
        ("Programming Fundamentals", "Ruby on Rails"),
        
        ("Programming Fundamentals", "Data Structures"),
        
        # Software Engineering
        ("Git", "GitHub"),
        ("Git", "Software Testing"),
        ("Software Testing", "Test-Driven Development"),
        ("Git", "Continuous Integration and Delivery"),
        
        ("Design Patterns", "Software Architecture"),
        ("Software Architecture", "System Design"),
        ("Software Architecture", "Distributed Systems"),
        
        # Backend
        ("Backend Development", "FastAPI"),
        ("Backend Development", "Django"),
        ("Backend Development", "Flask"),
        ("Backend Development", "Node.js"),
        
        ("Backend Development", "API Design"),
        
        ("Backend Development", "Authentication"),
        ("Authentication", "JWT"),
        ("Authentication", "Identity and Access Management"),
        
        ("Database Management", "Redis"),
        ("Database Management", "Message Queues"),
        ("Message Queues", "Microservices"),
        
        # Frontend
        ("JavaScript", "Frontend Development"),
        ("Frontend Development", "Tailwind CSS"),
        ("Frontend Development", "Web Accessibility"),
        ("Frontend Development", "State Management"),
        ("TypeScript", "Next.js"),
        ("React", "Next.js"),
        
        # Data
        ("Python", "Data Science"),
        ("Statistics & Probability", "Data Science"),
        ("Pandas", "Data Science"),
        ("NumPy", "Data Science"),
        ("Data Visualization", "Data Science"),
        
        ("Data Engineering", "Apache Spark"),
        ("Data Engineering", "Data Warehousing"),
        
        # AI/ML
        ("Artificial Intelligence", "Machine Learning"),
        ("Transformers", "Large Language Models"),
        ("Generative AI", "Retrieval-Augmented Generation"),
        
        ("Embeddings", "Retrieval-Augmented Generation"),
        ("Vector Databases", "Retrieval-Augmented Generation"),
        
        ("Large Language Models", "Prompt Engineering"),
        ("Large Language Models", "AI Agents"),
        ("Large Language Models", "Fine Tuning"),
        ("Large Language Models", "Model Evaluation"),
        
        # Cloud / DevOps
        ("Continuous Integration and Delivery", "Docker"),
        
        ("Cloud Computing", "Serverless"),
        
        # Cybersecurity
        ("Networking", "Cybersecurity"),
        ("Cybersecurity", "Application Security"),
        ("Application Security", "Security Testing"),
        ("Security Testing", "OWASP"),
        ("Cybersecurity", "Ethical Hacking"),
        
        # Mobile
        ("Mobile Development", "Android Development"),
        ("Mobile Development", "iOS Development"),
        ("Android Development", "Kotlin"),
        ("iOS Development", "Swift"),
        
        # Others
        ("Software Architecture", "Agile Methodology"),
        ("Agile Methodology", "Product Management"),
        ("Data Visualization", "Business Intelligence"),
        ("Frontend Development", "UI/UX Design"),
        
        # Full Stack
        ("Backend Development", "Full Stack Developer"),
        ("Frontend Development", "Full Stack Developer")
    ]
    
    # 3. Build current graph
    current_prereqs = db.query(SkillPrerequisite).all()
    print(f"Previous prerequisite count: {len(current_prereqs)}")
    
    graph = {}
    existing_edges = set()
    for p in current_prereqs:
        existing_edges.add((p.prerequisite_id, p.skill_id))
        graph.setdefault(p.prerequisite_id, []).append(p.skill_id)
        
    # 4. Filter and add new edges
    to_add = []
    for req_name, target_name in new_edges:
        req_id = skills.get(req_name)
        target_id = skills.get(target_name)
        
        if req_id and target_id:
            if (req_id, target_id) not in existing_edges:
                to_add.append((req_id, target_id))
                graph.setdefault(req_id, []).append(target_id)
        else:
            if not req_id:
                print(f"Warning: Prerequisite '{req_name}' not found.")
            if not target_id:
                print(f"Warning: Target '{target_name}' not found.")
                
    # 5. Cycle Detection
    if detect_cycles(graph):
        print("Aborting: Cycle detected in proposed graph.")
        return
        
    # 6. Commit
    for req_id, target_id in to_add:
        db.add(SkillPrerequisite(skill_id=target_id, prerequisite_id=req_id))
        
    db.commit()
    
    # 7. Verification Report
    all_prereqs = db.query(SkillPrerequisite).all()
    final_prereq_count = len(all_prereqs)
    
    skills_with_prereqs = set(p.skill_id for p in all_prereqs)
    roots = [sid for sid in skills.values() if sid not in skills_with_prereqs]
    
    isolated = []
    has_outgoing = set(p.prerequisite_id for p in all_prereqs)
    for sid in skills.values():
        if sid not in skills_with_prereqs and sid not in has_outgoing:
            isolated.append(sid)
            
    print("\n--- VERIFICATION REPORT ---")
    print(f"Previous Skill count: {len(skills)}")
    print(f"Final Skill count: {len(skills)}")
    print(f"Previous prerequisite count: {len(current_prereqs)}")
    print(f"Number of new prerequisites: {len(to_add)}")
    print(f"Final prerequisite count: {final_prereq_count}")
    print(f"Number of skills with prerequisites: {len(skills_with_prereqs)}")
    print(f"Number of root/foundational skills: {len(roots)}")
    print(f"Number of completely isolated skills: {len(isolated)}")
    print(f"Cycle count: 0 (Validated)")
    print(f"Duplicate relationship count: 0 (Idempotent filter applied)")
    
if __name__ == "__main__":
    seed_prerequisites()
