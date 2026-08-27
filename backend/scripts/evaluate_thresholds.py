import sys
import os
import json
import torch
from typing import List, Dict

sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from services.skill_mapping.semantic_matcher import SemanticMatcher
from models import Resource

def calculate_metrics(y_true: List[set], y_pred: List[set]):
    tp = 0
    fp = 0
    fn = 0
    
    for true_set, pred_set in zip(y_true, y_pred):
        tp += len(true_set.intersection(pred_set))
        fp += len(pred_set - true_set)
        fn += len(true_set - pred_set)
        
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1, tp, fp, fn

def evaluate_threshold(matcher, resources, candidates_list, ground_truth, threshold):
    matcher.threshold = threshold
    
    y_true = []
    y_pred = []
    
    unmapped = 0
    total_maps = 0
    groq_triggers = 0
    
    for i, cands in enumerate(candidates_list):
        high, ambiguous, low = matcher.resolve_candidates(cands)
        
        pred_set = set([c["skill_id"] for c in high])
        
        if ambiguous:
            groq_triggers += 1
            # Groq resolver simulation: it maps if true label has it
            true_set = set(ground_truth[resources[i].id])
            for a in ambiguous:
                if a["skill_id"] in true_set:
                    pred_set.add(a["skill_id"])
                    
        y_pred.append(pred_set)
        y_true.append(set(ground_truth[resources[i].id]))
        
        if not pred_set:
            unmapped += 1
        total_maps += len(pred_set)
        
    p, r, f1, tp, fp, fn = calculate_metrics(y_true, y_pred)
    return p, r, f1, fp, fn, unmapped, total_maps, groq_triggers

def main():
    db = SessionLocal()
    
    gt_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "llm_assisted_ground_truth.json")
    if not os.path.exists(gt_file):
        print("Ground truth file not found!")
        sys.exit(1)
        
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
        
    gt_map = {item["resource_id"]: item["expected_skill_ids"] for item in gt_data}
    
    resources = db.query(Resource).filter(Resource.id.in_(gt_map.keys())).all()
    resources.sort(key=lambda x: x.id)
    
    print(f"Loaded {len(resources)} resources with ground truth.")
    
    matcher = SemanticMatcher(SkillEmbeddingStore(db))
    
    print("Pre-computing embeddings...")
    texts = [f"{r.title}. {r.description}. Skills: " for r in resources]
    embeddings = matcher.embed_texts(texts)
    candidates_list = matcher.match_batch(embeddings)
    
    print("\n--- COARSE SEARCH ---")
    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50]
    
    best_f1 = -1
    best_t = 0.30
    
    print(f"{'Threshold':<10} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'FP':<4} | {'FN':<4} | {'Unmapped':<8} | {'Groq':<4}")
    print("-" * 75)
    
    for t in thresholds:
        p, r, f1, fp, fn, unmapped, total, groq = evaluate_threshold(matcher, resources, candidates_list, gt_map, t)
        print(f"{t:<10.2f} | {p:<6.2f} | {r:<6.2f} | {f1:<6.2f} | {fp:<4} | {fn:<4} | {unmapped:<8} | {groq:<4}")
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
            
    print(f"\nBest Coarse Threshold: {best_t:.2f} (F1: {best_f1:.2f})")
    
    print("\n--- FINE SEARCH ---")
    fine_thresholds = [best_t - 0.04, best_t - 0.03, best_t - 0.02, best_t - 0.01, best_t, best_t + 0.01, best_t + 0.02, best_t + 0.03, best_t + 0.04]
    
    best_fine_f1 = -1
    best_fine_t = best_t
    
    print(f"{'Threshold':<10} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'FP':<4} | {'FN':<4} | {'Unmapped':<8} | {'Groq':<4}")
    print("-" * 75)
    for t in fine_thresholds:
        p, r, f1, fp, fn, unmapped, total, groq = evaluate_threshold(matcher, resources, candidates_list, gt_map, t)
        print(f"{t:<10.2f} | {p:<6.2f} | {r:<6.2f} | {f1:<6.2f} | {fp:<4} | {fn:<4} | {unmapped:<8} | {groq:<4}")
        if f1 > best_fine_f1:
            if f1 == best_fine_f1:
                if t > best_fine_t:
                    best_fine_t = t
            else:
                best_fine_f1 = f1
                best_fine_t = t
                
    print(f"\nRecommended SKILL_SIMILARITY_THRESHOLD: {best_fine_t:.2f}")

if __name__ == "__main__":
    main()
