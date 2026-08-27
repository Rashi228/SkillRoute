import sys
sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from services.skill_mapping.mapper import SkillMapperOrchestrator
from models import Resource

db = SessionLocal()
mapper = SkillMapperOrchestrator(db)
res = db.query(Resource).filter(Resource.dataset_name == 'coursera .csv').first()

text = f'{res.title}. {res.description}. Skills: '
emb = mapper.semantic_matcher.embed_texts([text])
cands = mapper.semantic_matcher.match_batch(emb)[0]
for c in cands:
    print(f"{c['skill'].name}: {c['score']:.4f}")
