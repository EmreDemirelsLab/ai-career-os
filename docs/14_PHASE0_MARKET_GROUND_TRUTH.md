# 14 --- Phase 0 Market Ground Truth

## Status

Repo-entry baseline. This document converts initial 2026 market research
into seed contracts. It is not a statistically representative market
report yet.

## Initial evidence

Recent Germany/EU job samples show recurring bundles:

### Production ML

Python + PyTorch/TensorFlow + ML fundamentals + experiment tracking +
production deployment + Git/CI/CD + Docker/Kubernetes + cloud +
NumPy/Pandas/SQL.

### Applied LLM

Python + FastAPI/API integration + LLMs + RAG + vector databases +
LangChain/LangGraph/Semantic Kernel + PostgreSQL/Redis + Docker/Git.

### AI Platform / LLMOps

Kubernetes + IaC/GitOps + CI/CD + LLM serving/RAG/vector DB +
observability + security/IAM + performance/cost.

### Advanced agentic

LLM applications + tool calling + MCP + deterministic/agentic
orchestration + evaluation/tracing + governance/security + CI/CD.

These are seed observations, not frequency claims. Production analytics
must replace them with measured statistics.

## Role taxonomy v0.1

Primary: - AI Engineer - Applied AI Engineer - Machine Learning
Engineer - LLM/GenAI Engineer

Secondary: - MLOps/LLMOps Engineer - AI Platform Engineer - Data
Scientist

Long-horizon: - Applied Scientist - Research Scientist

## Skill pillars v0.1

1.  Software engineering foundation
2.  Data and SQL
3.  Mathematics/statistics/classical ML
4.  Deep learning/PyTorch
5.  LLM/RAG/evaluation
6.  Agentic systems/tool use/MCP
7.  Backend/API engineering
8.  MLOps/LLMOps
9.  Cloud/AWS
10. Production security/reliability/cost
11. Technical English/communication

## Hard eligibility dimensions

Store separately from skills: - mandatory degree - mandatory years of
professional experience - mandatory German/English level - work
authorization - location/onsite/travel - regulated license/security
clearance

## Critical architecture implication

Opportunity scoring must output: - eligibility status - capability fit -
evidence fit - preference fit - stretch level

A single match percentage is prohibited.

## Seed data files

-   `seed/role_taxonomy_v0.1.json`
-   `seed/skill_taxonomy_v0.1.json`
-   `seed/source_registry_seed.csv`

## What remains empirical after repo creation

The ingestion pipeline must collect enough records to calculate: -
frequency - growth - persistence - company-normalized demand -
source-normalized demand - role/seniority/geography splits -
English-only vs German-required distribution - degree requirement
distribution - co-occurrence clusters

Do not hard-code current sample observations as market truth.
