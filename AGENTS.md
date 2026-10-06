# AI Career OS implementation rules

Read docs/16_ARCHITECTURE_REVIEW_v1_3.md and docs/18_SPRINT1_ACCEPTANCE.md first, then the relevant baseline docs. For the personal workspace extension, read docs/21_COMPLETE_PRODUCT_CONTRACT.md and docs/22_WORKSPACE_VERIFICATION.md; preserve their explicit incomplete-product gates. Preserve the dated original design and seed semantics. No unmeasured market statistics; no personal learner data in this public repo. All future source text is untrusted. Foundation before extraction/agents. Do not infer learner mastery from generated code. Run checks and report skipped gates honestly. No automatic deployment or merge.

For intelligence-engine work, docs/23_INTELLIGENCE_RELEASE.md is the current v1.4 implementation and release boundary. Mocked AI/collector tests do not establish live quality or source approval.

Continuity: at the start of a resumed task, read CONTINUITY.md and docs/25_DELIVERY_PLAN.md, verify the remote head/checks, and continue the recorded active part. Before pausing, update the checkpoint with the exact verified result and next action. Do not mark pending gates complete.

For retention work, docs/26_RETENTION_CONTRACT.md governs owner/runtime separation and derived data. Never run maintenance on real user data while implementing/testing this part; use disposable fixtures.
