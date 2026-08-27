import sys
import os
import torch

sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from services.skill_mapping.semantic_matcher import SemanticMatcher
from services.skill_mapping.llm_resolver import LLMResolver

def test_cases():
    db = SessionLocal()
    matcher = SemanticMatcher(SkillEmbeddingStore(db))
    resolver = LLMResolver()
    
    # We set threshold to 0.36 for our tests as recommended
    matcher.threshold = 0.36
    matcher.ambiguity_margin = 0.06
    
    print(f"Testing with Threshold: {matcher.threshold}, Ambiguity Margin: {matcher.ambiguity_margin}\n")
    
    # Case A: Top1 clearly stronger than Top2
    print("--- Case A: Top1 Clearly Stronger ---")
    case_a_text = "Learn exactly how to build REST APIs with Node.js and Express. Master backend JavaScript development."
    emb_a = matcher.embed_texts([case_a_text])
    cands_a = matcher.match_batch(emb_a)[0]
    high_a, ambig_a, low_a = matcher.resolve_candidates(cands_a)
    
    print("Top Candidates:")
    for c in cands_a[:3]:
        print(f"  {c['skill'].name}: {c['score']:.4f}")
        
    print(f"Resolved High Confidence: {[c['skill'].name for c in high_a]}")
    print(f"Resolved Ambiguous: {[c['skill'].name for c in ambig_a]}")
    if not ambig_a:
        print("-> SUCCESS: Automatic mapping, no Groq invoked.\n")
    else:
        print("-> FAILED: Groq would be invoked.\n")
        
    # Case B: Top1 and Top2 very close
    print("--- Case B: Top1 and Top2 Close ---")
    case_b_text = "Mastering both Python and Java for Backend Services. Build scalable web architectures."
    emb_b = matcher.embed_texts([case_b_text])
    cands_b = matcher.match_batch(emb_b)[0]
    high_b, ambig_b, low_b = matcher.resolve_candidates(cands_b)
    
    print("Top Candidates:")
    for c in cands_b[:3]:
        print(f"  {c['skill'].name}: {c['score']:.4f}")
        
    print(f"Resolved High Confidence: {[c['skill'].name for c in high_b]}")
    print(f"Resolved Ambiguous: {[c['skill'].name for c in ambig_b]}")
    if ambig_b:
        print("-> SUCCESS: Groq invoked for ambiguity resolution.")
        # Simulating Groq
        print(f"Simulating Groq call with {len(ambig_b)} candidates...")
        # (We skip actual Groq call here to save time and API keys, just proving the router)
    else:
        print("-> FAILED: Ambiguity margin not triggered.\n")
        
    # Case C: All candidates below threshold
    print("\n--- Case C: All candidates weak (Reject) ---")
    case_c_text = "Introduction to 18th Century French Literature and Poetry."
    emb_c = matcher.embed_texts([case_c_text])
    cands_c = matcher.match_batch(emb_c)[0]
    high_c, ambig_c, low_c = matcher.resolve_candidates(cands_c)
    
    print("Top Candidates:")
    for c in cands_c[:3]:
        print(f"  {c['skill'].name}: {c['score']:.4f}")
        
    print(f"Resolved High Confidence: {[c['skill'].name for c in high_c]}")
    print(f"Resolved Ambiguous: {[c['skill'].name for c in ambig_c]}")
    if not high_c and not ambig_c:
        print("-> SUCCESS: Rejected/Unmapped, no Groq invoked.\n")
    else:
        print("-> FAILED: Erroneously mapped something.\n")

if __name__ == "__main__":
    test_cases()
