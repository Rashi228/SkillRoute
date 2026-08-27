import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models import Skill

class AliasManager:
    def __init__(self, db: Session):
        self.db = db
        self.exact_map = {}
        self._load_vocabulary()
        
    def _load_vocabulary(self):
        """Loads all skill names and their aliases into a fast lookup map."""
        skills = self.db.query(Skill).all()
        for skill in skills:
            # Primary name
            self.exact_map[skill.name.lower().strip()] = skill.id
            
            # Aliases
            if skill.aliases:
                try:
                    aliases_list = json.loads(skill.aliases)
                    for alias in aliases_list:
                        self.exact_map[alias.lower().strip()] = skill.id
                except Exception:
                    pass

    def get_skill_id(self, term: str) -> Optional[int]:
        """Returns the skill ID if the term matches exactly or via an alias."""
        term_clean = term.lower().strip()
        return self.exact_map.get(term_clean)
