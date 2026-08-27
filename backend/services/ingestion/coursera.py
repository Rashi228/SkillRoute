from .base import ProviderAdapter, NormalizedResource
import re

class CourseraAdapter(ProviderAdapter):
    def normalize_row(self, row: dict) -> NormalizedResource:
        course_id = row.get("course_id", "").strip()
        title = (row.get("course_title") or row.get("title", "")).strip()
        if not title:
            raise ValueError("Row missing title")
            
        url = (row.get("course_url") or row.get("url", "")).strip()
        if not url:
            raise ValueError("Row missing url")
            
        # Clean URL to canonical form
        canonical_url = url.split("?")[0].strip("/")
        if not canonical_url:
            canonical_url = None
            
        difficulty_map = {
            "beginner": "BEGINNER",
            "intermediate": "INTERMEDIATE",
            "advanced": "ADVANCED",
            "mixed": "UNKNOWN"
        }
        raw_diff = (row.get("course_difficulty") or row.get("difficulty", "")).lower().strip()
        difficulty = difficulty_map.get(raw_diff, "UNKNOWN")
        
        # Default Coursera is usually a course and often has free audit
        raw_skills = []
        skills_str = (row.get("course_skills") or row.get("skills", ""))
        if skills_str:
            raw_skills = [s.strip() for s in skills_str.split(",") if s.strip()]

        rating = None
        try:
            r_str = row.get("course_rating") or row.get("rating")
            if r_str: rating = float(r_str)
        except:
            pass

        review_count = None
        try:
            rev_str = row.get("course_reviews_num") or row.get("review_count")
            if rev_str: review_count = int(rev_str)
        except:
            pass
            
        metadata = {}
        exclude_keys = ["course_id", "title", "url", "difficulty", "skills", "rating", "review_count", 
                        "course_title", "course_url", "course_difficulty", "course_skills", "course_rating", "course_reviews_num", "course_description"]
        for k, v in row.items():
            if k not in exclude_keys:
                metadata[k] = v

        desc = (row.get("course_description") or row.get("description", "")).strip()

        return NormalizedResource(
            external_id=course_id if course_id else None,
            provider="Coursera",
            canonical_url=canonical_url,
            title=title,
            description=desc,
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
