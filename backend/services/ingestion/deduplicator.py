from sqlalchemy.orm import Session
from models import Resource
from .base import NormalizedResource

class Deduplicator:
    def __init__(self, db: Session):
        self.db = db

    def find_existing(self, resource: NormalizedResource) -> Resource:
        """
        Level 1: Match by provider + external_id
        Level 2: Match by canonical_url
        Returns the existing Resource object, or None if new.
        """
        # Level 1: Provider + External ID
        if resource.external_id and resource.provider:
            existing = self.db.query(Resource).filter(
                Resource.provider == resource.provider,
                Resource.external_id == resource.external_id
            ).first()
            if existing:
                return existing
                
        # Level 2: Canonical URL
        if resource.canonical_url:
            existing = self.db.query(Resource).filter(
                Resource.canonical_url == resource.canonical_url
            ).first()
            if existing:
                return existing
                
        return None
