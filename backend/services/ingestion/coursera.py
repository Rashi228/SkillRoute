from .base import ProviderAdapter, NormalizedResource
import re

class CourseraAdapter(ProviderAdapter):
    def normalize_row(self, row: dict) -> NormalizedResource:
        course_id = row.get("course_id", "").strip()
        title = row.get("title", "").strip()
        url = row.get("url", "").strip()
        
        # Clean URL to canonical form
        canonical_url = url.split("?")[0].strip("/")
        
        difficulty_map = {
            "beginner": "BEGINNER",
            "intermediate": "INTERMEDIATE",
            "advanced": "ADVANCED",
            "mixed": "UNKNOWN"
        }
        raw_diff = row.get("difficulty", "").lower().strip()
        difficulty = difficulty_map.get(raw_diff, "UNKNOWN")
        
        # Default Coursera is usually a course and often has free audit
        raw_skills = []
        skills_str = row.get("skills", "")
        if skills_str:
            raw_skills = [s.strip() for s in skills_str.split(",") if s.strip()]

        rating = None
        try:
            rating = float(row.get("rating", 0))
        except:
            pass

        review_count = None
        try:
            review_count = int(row.get("review_count", 0))
        except:
            pass
            
        metadata = {}
        for k, v in row.items():
            if k not in ["course_id", "title", "url", "difficulty", "skills", "rating", "review_count"]:
                metadata[k] = v

        return NormalizedResource(
            external_id=course_id if course_id else None,
            provider="Coursera",
            canonical_url=canonical_url,
            title=title,
            description=row.get("description", "").strip(),
            resource_type="COURSE",
            url=url,
            difficulty=difficulty,
            language=row.get("language", "English"),
            # Cost classification happens in normalizer layer later
            rating=rating,
            review_count=review_count,
            metadata_json=metadata,
            source=self.source,
            dataset_name=self.dataset_name,
            dataset_version=self.dataset_version,
            raw_skills=raw_skills
        )
