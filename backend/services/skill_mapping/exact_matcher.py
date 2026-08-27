from typing import List, Tuple, Set
from services.skill_mapping.aliases import AliasManager
from models import Resource

class ExactMatcher:
    def __init__(self, alias_manager: AliasManager):
        self.alias_manager = alias_manager
        
    def match_provider_skills(self, provider_skills: List[str]) -> List[Tuple[int, float, str]]:
        """
        Takes raw provider skills and returns matched DB skill IDs.
        Returns: List of (skill_id, confidence, mapping_source)
        """
        matched = []
        seen = set()
        for raw_skill in provider_skills:
            skill_id = self.alias_manager.get_skill_id(raw_skill)
            if skill_id and skill_id not in seen:
                # Is it an exact match or an alias match? 
                # (For simplicity, we tag them both as EXACT_MATCH/ALIAS_MATCH, we can treat them identically here 
                # as EXPLICIT_PROVIDER since the provider explicitly tagged it and it matches our DB).
                matched.append((skill_id, 1.0, "EXPLICIT_PROVIDER"))
                seen.add(skill_id)
                
        return matched
