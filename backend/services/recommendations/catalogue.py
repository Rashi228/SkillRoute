import json
from typing import Dict, Any, List

# Centralized curated mapping for authentic platforms and documentation.
# Keys can be exact skill names or lowercase simplified names.

PRACTICE_CATALOGUE = {
    "data structures": [
        {"platform": "LeetCode", "url": "https://leetcode.com/", "cost": "FREEMIUM", "why": "Industry standard for DSA problems."},
        {"platform": "HackerRank", "url": "https://www.hackerrank.com/", "cost": "FREEMIUM", "why": "Structured learning paths for algorithms."}
    ],
    "machine learning": [
        {"platform": "Kaggle", "url": "https://www.kaggle.com/", "cost": "FREE", "why": "Datasets, notebooks, and ML competitions."}
    ],
    "python": [
        {"platform": "Exercism", "url": "https://exercism.org/tracks/python", "cost": "FREE", "why": "Mentored practice problems for Python."},
        {"platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "cost": "FREE", "why": "Interactive Python curriculum."}
    ],
    "web development": [
        {"platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "cost": "FREE", "why": "Comprehensive interactive web dev courses."}
    ],
    "react": [
        {"platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "cost": "FREE", "why": "Frontend libraries certification."}
    ]
}

DOCUMENTATION_CATALOGUE = {
    "python": [
        {"title": "Python Official Documentation", "url": "https://docs.python.org/3/", "type": "Documentation", "source": "python.org"}
    ],
    "react": [
        {"title": "React Official Documentation", "url": "https://react.dev/", "type": "Documentation", "source": "react.dev"}
    ],
    "docker": [
        {"title": "Docker Official Documentation", "url": "https://docs.docker.com/", "type": "Documentation", "source": "docker.com"}
    ],
    "kubernetes": [
        {"title": "Kubernetes Official Documentation", "url": "https://kubernetes.io/docs/home/", "type": "Documentation", "source": "kubernetes.io"}
    ],
    "fastapi": [
        {"title": "FastAPI Official Documentation", "url": "https://fastapi.tiangolo.com/", "type": "Documentation", "source": "tiangolo.com"}
    ],
    "machine learning": [
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "Documentation", "source": "google.com"}
    ],
    "data structures": [
        {"title": "GeeksforGeeks DSA", "url": "https://www.geeksforgeeks.org/data-structures/", "type": "Article", "source": "geeksforgeeks.org"}
    ]
}

def get_practice_platforms(skill_name: str) -> List[Dict[str, str]]:
    skill_lower = skill_name.lower()
    # Fuzzy match or exact match
    for key, platforms in PRACTICE_CATALOGUE.items():
        if key in skill_lower or skill_lower in key:
            return platforms
    return []

def get_documentation(skill_name: str) -> List[Dict[str, str]]:
    skill_lower = skill_name.lower()
    for key, docs in DOCUMENTATION_CATALOGUE.items():
        if key in skill_lower or skill_lower in key:
            return docs
    return []
