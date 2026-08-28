from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class CostType(str, enum.Enum):
    FREE = "FREE"
    FREE_AUDIT = "FREE_AUDIT"
    FREEMIUM = "FREEMIUM"
    TRIAL = "TRIAL"
    PAID = "PAID"
    UNKNOWN = "UNKNOWN"

class VerificationStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    STALE = "STALE"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String)
    dataset_name = Column(String)
    dataset_version = Column(String)
    dry_run = Column(Boolean, default=False)
    status = Column(String, default="PENDING")
    
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    inserted_rows = Column(Integer, default=0)
    updated_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    validation_failed_rows = Column(Integer, default=0)
    unknown_url_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    # Skill Mapping Metrics
    exact_matches = Column(Integer, default=0)
    alias_matches = Column(Integer, default=0)
    semantic_matches = Column(Integer, default=0)
    groq_reviewed = Column(Integer, default=0)
    unmapped_resources = Column(Integer, default=0)
    total_mappings = Column(Integer, default=0)
    total_confidence_sum = Column(Float, default=0.0)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_goal = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    time_commitment = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")
    passports = relationship("LearnerSkill", back_populates="profile")
    paths = relationship("LearningPath", back_populates="profile")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    aliases = Column(Text, nullable=True) # Stored as JSON array
    parent_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    
    # Embeddings (JSON text for now, cleanly migratable to pgvector later)
    embedding = Column(Text, nullable=True) 
    embedding_model = Column(String, nullable=True)
    embedding_version = Column(String, nullable=True)
    embedding_content_hash = Column(String, nullable=True)
    embedding_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)

class LearnerSkill(Base):
    __tablename__ = "learner_skills"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    confidence_score = Column(Float, default=0.0) # 0 to 100
    status = Column(String, default="Missing") # Mastered, Developing, Missing
    evidence_source = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="passports")
    skill = relationship("Skill")

class UserSkillProgress(Base):
    __tablename__ = "user_skill_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    status = Column(String, default="INCOMPLETE") # COMPLETED, INCOMPLETE
    mastery_score = Column(Float, default=0.0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User")
    skill = relationship("Skill")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    
    # Identity
    external_id = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    canonical_url = Column(String, unique=True, index=True, nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String) # COURSE, VIDEO, PROJECT, etc.
    url = Column(String)
    final_url = Column(String, nullable=True)
    
    difficulty = Column(String)
    duration_hours = Column(Float, default=1.0)
    language = Column(String, nullable=True)
    
    # Cost
    cost_type = Column(Enum(CostType), default=CostType.UNKNOWN)
    price_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    
    # Metrics
    quality_score = Column(Float, default=0.0)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    popularity_score = Column(Float, nullable=True)
    
    # External Metadata
    thumbnail_url = Column(String, nullable=True)
    video_id = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True) # Stored as JSON string
    
    # Validation & Status
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.UNKNOWN)
    last_verified = Column(DateTime(timezone=True), server_default=func.now())
    http_status = Column(Integer, nullable=True)
    validation_error = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Provenance
    source = Column(String, nullable=True)
    dataset_name = Column(String, nullable=True)
    dataset_version = Column(String, nullable=True)
    ingestion_job_id = Column(Integer, ForeignKey("ingestion_jobs.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ResourceSkill(Base):
    __tablename__ = "resource_skills"
    resource_id = Column(Integer, ForeignKey("resources.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    confidence = Column(Float, nullable=True)
    mapping_source = Column(String, nullable=True)

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    route_type = Column(String) # Balanced, Fast, Deep Theory, Project-Based
    estimated_duration = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="Active")

    profile = relationship("Profile", back_populates="paths")
    nodes = relationship("PathNode", back_populates="path")

class PathNode(Base):
    __tablename__ = "path_nodes"
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    order_index = Column(Integer)
    status = Column(String, default="Locked") # Locked, In Progress, Completed

    path = relationship("LearningPath", back_populates="nodes")
    resource = relationship("Resource")

# Phase 1.9 / AMPlified Additions

class ExplanationCache(Base):
    """Caches grounded RAG explanations for node prerequisites."""
    __tablename__ = "explanation_cache"
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), index=True)
    target_goal = Column(String, index=True)
    explanation_text = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class PathTransition(Base):
    """OPTIONAL schema for tracking real user transitions for future collaborative filtering."""
    __tablename__ = "path_transitions"
    id = Column(Integer, primary_key=True, index=True)
    from_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    to_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    count = Column(Integer, default=1)
    
class UserSkillStreak(Base):
    """Schema for future gamification tracking."""
    __tablename__ = "user_skill_streaks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime(timezone=True), nullable=True)

