from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any

class NormalizedResource(BaseModel):
    external_id: Optional[str] = None
    provider: str
    canonical_url: str
    title: str
    description: Optional[str] = None
    resource_type: str = "COURSE"
    url: str
    difficulty: Optional[str] = None
    duration_hours: float = 1.0
    language: Optional[str] = None
    cost_type: str = "UNKNOWN"
    price_amount: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    popularity_score: Optional[float] = None
    thumbnail_url: Optional[str] = None
    metadata_json: Dict[str, Any] = {}
    source: str
    dataset_name: Optional[str] = None
    dataset_version: Optional[str] = None
    raw_skills: List[str] = [] # Skills from the provider to be mapped
    
    # Validation fields
    final_url: Optional[str] = None
    verification_status: str = "UNKNOWN"
    http_status: Optional[int] = None
    validation_error: Optional[str] = None

class ProviderAdapter:
    def __init__(self, source: str, dataset_name: str, dataset_version: str):
        self.source = source
        self.dataset_name = dataset_name
        self.dataset_version = dataset_version

    def normalize_row(self, row: dict) -> NormalizedResource:
        """Translates a raw dictionary from the dataset into the Normalized schema."""
        raise NotImplementedError
