import os
import sys
import argparse
import time
import uuid
import datetime

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal
from models import IngestionJob
from services.ingestion.pipeline import IngestionPipeline
from services.ingestion.coursera import CourseraAdapter

def print_report(job: IngestionJob, duration: float):
    print("\n" + "="*48)
    print("SkillRoute Resource Ingestion".center(48))
    print("="*48)
    print(f"Source: {job.source}")
    print(f"Dataset: {job.dataset_name} ({job.dataset_version})")
    print(f"Job ID: {job.job_id}")
    print(f"Mode: {'DRY RUN' if job.dry_run else 'PRODUCTION'}")
    print("\nRows discovered:".ljust(30) + str(job.total_rows).rjust(15))
    print("Rows normalized:".ljust(30) + str(job.processed_rows).rjust(15))
    print("Duplicates:".ljust(30) + str(job.duplicate_rows).rjust(15))
    print("Invalid rows:".ljust(30) + str(job.invalid_rows).rjust(15))
    print("Errors:".ljust(30) + str(job.error_rows).rjust(15))
    
    print("\nURL validation:")
    # We can infer VERIFIED if they didn't fail or return unknown
    verified = job.processed_rows - (job.validation_failed_rows + job.unknown_url_rows)
    if job.dry_run:
        print("  (Skipped in dry run mode)")
    else:
        print("Verified:".ljust(30) + str(verified).rjust(15))
        print("Failed:".ljust(30) + str(job.validation_failed_rows).rjust(15))
        print(f"Unknown:                               {job.unknown_url_rows:8d}")
    print("\nDatabase:")
    print(f"Inserted:                              {job.inserted_rows:8d}")
    print(f"Updated:                               {job.updated_rows:8d}")
    
    print("\nSkill Mapping")
    print("-" * 48)
    print(f"Exact matches:                         {job.exact_matches:8d}")
    print(f"Alias matches:                         {job.alias_matches:8d}")
    print(f"Semantic matches:                      {job.semantic_matches:8d}")
    print(f"Groq reviewed:                         {job.groq_reviewed:8d}")
    print(f"Unmapped:                              {job.unmapped_resources:8d}")
    print("-" * 48)
    print(f"Total mappings:                        {job.total_mappings:8d}")
    
    avg_conf = job.total_confidence_sum / job.total_mappings if job.total_mappings > 0 else 0.0
    print(f"Average confidence:                    {avg_conf:8.2f}")
    
    print(f"\nDuration: {duration:.2f} seconds")
    print(f"Status: {job.status}")
    if job.error_message:
        print("\nJob Error Details:")
        print(job.error_message)
    print("="*48 + "\n")

def main():
    parser = argparse.ArgumentParser(description="SkillRoute Resource Data Ingestion Pipeline")
    parser.add_argument("--source", type=str, required=True, help="Provider (e.g., coursera)")
    parser.add_argument("--file", type=str, required=True, help="Path to raw dataset file")
    parser.add_argument("--dry-run", action="store_true", help="Parse and process without DB mutation")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for DB upserts")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
        
    db = SessionLocal()
    
    # Create Job Record
    job_id = str(uuid.uuid4())
    job = IngestionJob(
        job_id=job_id,
        source=args.source.title(),
        dataset_name=os.path.basename(args.file),
        dataset_version="v1",
        dry_run=args.dry_run,
        status="PENDING"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    print(f"Starting ingestion job: {job_id}")
    
    if args.source.lower() == "coursera":
        adapter = CourseraAdapter(job.source, job.dataset_name, job.dataset_version)
    else:
        print(f"Error: Unsupported source '{args.source}'. Only 'coursera' is supported in Phase 1.")
        job.status = "FAILED"
        job.error_message = f"Unsupported source: {args.source}"
        db.commit()
        sys.exit(1)
        
    pipeline = IngestionPipeline(db, job_id, args.dry_run)
    
    start_time = time.time()
    try:
        pipeline.process_csv(args.file, adapter, args.batch_size)
    finally:
        job.completed_at = datetime.datetime.utcnow()
        db.commit()
        duration = time.time() - start_time
        db.refresh(job)
        print_report(job, duration)
        db.close()

if __name__ == "__main__":
    main()
