# Applied AI engineering practice: weeks 9–24

Work in `exercises.py`. Read the selected function docstring, lesson and checks; implement before reading `reference.py`. All inputs are synthetic and all operations are local.

```sh
uv sync --locked --group labs
uv run python labs/applied_ai/check.py --week 9
uv run python labs/applied_ai/check.py --reference
```

The starter intentionally fails. Reference mode verifies worked solutions, not your skill. Add a counterexample beyond the supplied cases and explain it in English without the reference.

| Week | Exercise | Acceptance focus |
| --- | --- | --- |
| 9 | loss_gradient | MSE derivative matches finite difference; finite aligned data |
| 10 | train_linear | Validation labels never affect training updates |
| 11 | experiment_id | Stable canonical identity; data/code provenance included |
| 12 | predict_batch | Versioned bounded inference; invalid numbers rejected |
| 13 | pack_context | Token-ID chunk packing reserves answer budget |
| 14 | cosine_rank | Normalized similarity, deterministic ties, invalid vectors |
| 15 | validate_citations | Exact quote provenance, empty/unknown citation rejection |
| 16 | retrieval_eval | Complete case set, separate recall/abstention denominators |
| 17 | dispatch_read | Strict read-only allowlist; no source instruction execution |
| 18 | retry_delay | Transient-status policy and three-attempt cap |
| 19 | compare_candidate | Same evaluation version, quality gain and cost ceiling |
| 20 | request_cost | Operator-supplied token rates and explicit units |
| 21 | safe_event | Only enum status and numeric duration may enter logs |
| 22 | service_summary | Sample count, error rate, nearest-rank p95, empty data |
| 23 | decision_gaps | ADR structural completeness, not semantic quality |
| 24 | claim_inventory | Artifact provenance and assistance; no verified-skill claim |

## Beyond these small checks

These exercises teach boundaries; they are not neural network training, a tokenizer, an embedding model, an LLM, full RAG, a production inference endpoint or independent educational evaluation. Weeks 9–10 additionally require the linked PyTorch autograd/optimization tutorial with tensors and separate train/validation behavior. Week 12 asks you to wrap inference in the foundation FastAPI exercise. Weeks 13–16 require real tokenizer/embedding/retrieval evaluation experiments before claiming model proficiency. No package/model is downloaded by these labs.

For each milestone submit code, failed-then-fixed test, assistance level, a short English defense and an independent reviewer’s feedback. Automated checks inspect specified examples; they cannot assess comprehension, originality, statistical validity or production readiness.
