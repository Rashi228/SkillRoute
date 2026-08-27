import csv
import traceback
import json
from typing import List
from sqlalchemy.orm import Session
from models import IngestionJob, Resource, ResourceSkill
from .base import ProviderAdapter, NormalizedResource
from .normalizer import CostClassifier
from services.skill_mapping.mapper import SkillMapperOrchestrator
from .deduplicator import Deduplicator
from .validator import validate_resources_sync

class IngestionPipeline:
    def __init__(self, db: Session, job_id: str, dry_run: bool = False):
        self.db = db
        self.job_id = job_id
        self.dry_run = dry_run
        
        # Load Job
        self.job = self.db.query(IngestionJob).filter(IngestionJob.job_id == job_id).first()
        if not self.job:
            raise ValueError(f"Job {job_id} not found")
            
        self.deduplicator = Deduplicator(self.db)
        self.skill_mapper = SkillMapperOrchestrator(self.db)

    def process_csv(self, file_path: str, adapter: ProviderAdapter, batch_size: int = 500):
        self.job.status = "RUNNING"
        self.db.commit()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    self.job.total_rows += 1
                    batch.append(row)
                    
                    if len(batch) >= batch_size:
                        self._process_batch(batch, adapter)
                        batch = []
                        
                if batch:
                    self._process_batch(batch, adapter)
                    
            self.job.status = "COMPLETED"
        except Exception as e:
            self.job.status = "FAILED"
            self.job.error_message = str(e) + "\n" + traceback.format_exc()
        finally:
            self.db.commit()

    def _process_batch(self, raw_rows: List[dict], adapter: ProviderAdapter):
        normalized_batch = []
        for row in raw_rows:
            self.job.processed_rows += 1
            try:
                norm_res = adapter.normalize_row(row)
                norm_res = CostClassifier.classify(norm_res, row)
                normalized_batch.append(norm_res)
            except Exception as e:
                self.job.invalid_rows += 1
                self.job.error_rows += 1
                print(f"Error normalizing row: {e}")
                # Skip invalid rows

        if not self.dry_run and normalized_batch:
            # URL Validation (Concurrent Batch)
            try:
                validate_resources_sync(normalized_batch, concurrency=10)
            except Exception as e:
                print(f"Validation batch failed: {e}")

        # DB Upsert
        inserted_resources = []
        successful_norm_res = []
        for norm_res in normalized_batch:
            if not self.dry_run:
                if norm_res.verification_status == "VERIFIED":
                    pass
                elif norm_res.verification_status == "FAILED":
                    self.job.validation_failed_rows += 1
                elif norm_res.verification_status == "UNKNOWN":
                    self.job.unknown_url_rows += 1

            try:
                if not self.dry_run:
                    with self.db.begin_nested():
                        res_obj = self._upsert_resource(norm_res)
                        if res_obj:
                            inserted_resources.append(res_obj)
                            successful_norm_res.append(norm_res)
                else:
                    self._upsert_resource(norm_res)
            except Exception as e:
                self.job.error_rows += 1
                print(f"Upsert failed for {norm_res.title}: {e}")
                
        # Map skills in batch
        if not self.dry_run and successful_norm_res:
            try:
                batch_mappings = self.skill_mapper.process_batch(successful_norm_res)
                for res_obj, mappings in zip(inserted_resources, batch_mappings):
                    if not mappings:
                        self.job.unmapped_resources += 1
                    for skill_id, conf, source in mappings:
                        self.job.total_mappings += 1
                        self.job.total_confidence_sum += conf
                        
                        if source in ["EXPLICIT_PROVIDER", "EXACT_MATCH"]:
                            self.job.exact_matches += 1
                        elif source == "ALIAS_MATCH":
                            self.job.alias_matches += 1
                        elif source == "SEMANTIC":
                            self.job.semantic_matches += 1
                        elif source == "LLM_REVIEW":
                            self.job.groq_reviewed += 1
                            
                        existing_rs = self.db.query(ResourceSkill).filter(
                            ResourceSkill.resource_id == res_obj.id,
                            ResourceSkill.skill_id == skill_id
                        ).first()
                        
                        if existing_rs:
                            if existing_rs.mapping_source != "EXPLICIT_PROVIDER" and source == "EXPLICIT_PROVIDER":
                                existing_rs.mapping_source = source
                                existing_rs.confidence = conf
                        else:
                            self.db.add(ResourceSkill(
                                resource_id=res_obj.id,
                                skill_id=skill_id,
                                confidence=conf,
                                mapping_source=source
                            ))
            except Exception as e:
                print(f"Error mapping batch: {e}")
                
        # Commit batch
        if not self.dry_run:
            self.db.commit()

    def _upsert_resource(self, norm_res: NormalizedResource):
        existing = self.deduplicator.find_existing(norm_res)
        
        if existing:
            changed = False
            # Check for changes (Idempotency)
            if existing.price_amount != norm_res.price_amount:
                existing.price_amount = norm_res.price_amount
                changed = True
                
            ex_status = existing.verification_status.value if hasattr(existing.verification_status, 'value') else existing.verification_status
            if ex_status != norm_res.verification_status:
                existing.verification_status = norm_res.verification_status
                changed = True
                
            if existing.title != norm_res.title:
                existing.title = norm_res.title
                changed = True
                
            if changed:
                self.job.updated_rows += 1
            else:
                self.job.duplicate_rows += 1
                
            resource_obj = existing
        else:
            # Insert new
            self.job.inserted_rows += 1
            if self.dry_run:
                return
                
            resource_obj = Resource(
                external_id=norm_res.external_id,
                provider=norm_res.provider,
                canonical_url=norm_res.canonical_url,
                title=norm_res.title,
                description=norm_res.description,
                resource_type=norm_res.resource_type,
                url=norm_res.url,
                final_url=norm_res.final_url,
                difficulty=norm_res.difficulty,
                language=norm_res.language,
                cost_type=norm_res.cost_type,
                price_amount=norm_res.price_amount,
                currency=norm_res.currency,
                rating=norm_res.rating,
                review_count=norm_res.review_count,
                metadata_json=json.dumps(norm_res.metadata_json),
                verification_status=norm_res.verification_status,
                http_status=norm_res.http_status,
                validation_error=norm_res.validation_error,
                source=norm_res.source,
                dataset_name=norm_res.dataset_name,
                dataset_version=norm_res.dataset_version,
                ingestion_job_id=self.job.id
            )
            self.db.add(resource_obj)
            self.db.flush() # get ID

        return resource_obj
