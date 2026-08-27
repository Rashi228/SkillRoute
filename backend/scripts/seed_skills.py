import sys
import os
sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from models import Skill
import json

db = SessionLocal()
new_skills = [
    ('Data Science', 'Extracting knowledge and insights from data using statistics and machine learning', '["Data Analytics", "Data Mining"]'),
    ('Deep Learning', 'Neural networks with multiple layers for learning complex patterns', '["Neural Networks", "DNN", "CNN"]'),
    ('Web Development', 'Building and maintaining websites and web applications', '["Frontend", "Backend", "Full Stack"]'),
    ('Cloud Computing', 'Delivery of computing services over the internet', '["AWS", "Azure", "GCP", "Cloud Architecture"]'),
    ('Cybersecurity', 'Protecting computer systems and networks from information disclosure and damage', '["Information Security", "Infosec", "Network Security"]'),
    ('Database Management', 'Storing, retrieving and managing data in databases', '["SQL", "NoSQL", "Relational Databases"]'),
    ('Generative AI', 'AI that can create new content like text, images, and code', '["GenAI", "LLMs", "Large Language Models"]')
]

for name, desc, aliases in new_skills:
    if not db.query(Skill).filter(Skill.name == name).first():
        db.add(Skill(name=name, description=desc, aliases=aliases))
db.commit()
print('Added test skills.')
