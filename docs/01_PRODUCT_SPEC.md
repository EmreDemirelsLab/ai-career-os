# 01 --- Product Specification

## 1. Product

**Working name:** AI Career OS

A market-intelligence and adaptive-learning platform for people
targeting AI/ML careers. It combines labor-market data, skill ontology,
learner evidence, curriculum generation, technical-English training,
portfolio building, interview simulation, certifications and application
outcomes.

## 2. Initial user and target

Initial target: - Germany first, EU/remote second, Türkiye as comparison
market. - Roles: AI Engineer, ML Engineer, Applied AI Engineer,
LLM/GenAI Engineer, MLOps/LLMOps Engineer, Data Scientist, Applied
Scientist, selected AI Solutions/Forward Deployed roles. - Initial
learner objective: become employable for AI/ML engineering roles while
improving technical English toward C1 comprehension and clear B2/C1
professional speaking.

The product must not assume a computer-science or engineering degree.
Education requirements must be represented as explicit job constraints:
`required`, `preferred`, `equivalent_experience_accepted`, `unknown`.

## 3. Jobs to be done

### Market intelligence

-   What skills are employers asking for now?
-   Which are foundational, persistent, accelerating or emerging?
-   Which skills co-occur as real-world stacks?
-   How do Germany, EU, remote and Türkiye differ?
-   Which requirements are hard filters versus preferences?

### Career planning

-   Which target role is closest to my current evidence?
-   What are my critical gaps?
-   What should I learn next and why?
-   What can I safely postpone?
-   Which certification is worth the time for my target roles?

### Learning

-   Teach difficult AI/ML concepts for understanding, not memorization.
-   Start in Turkish when concept load is high.
-   Transition the same concept to English.
-   Train sentence parsing, listening, explanation and interview
    communication.
-   Use spaced retrieval and progressively harder transfer tasks.

### Evidence

-   Prove skills with projects, code, deployment, tests, production
    experience, certifications and interview performance.
-   Convert projects into hiring evidence.

### Applications

-   Decide which roles are worth applying to.
-   Track application stages.
-   Learn from interview/rejection/offer outcomes.

## 4. Core user journey

1.  User selects target geography and roles.
2.  User imports/enters existing skills, projects and evidence.
3.  Market engine produces a dated market snapshot.
4.  Gap engine compares target role requirements with evidence.
5.  Roadmap engine creates a dependency-aware plan.
6.  Daily learning engine selects the next learning unit.
7.  User learns conceptually in Turkish when necessary.
8.  User consumes the same technical subject in English.
9.  System tests recall, code, debugging, system design and explanation.
10. Evidence graph is updated only from scored evidence.
11. Interview engine tests role readiness.
12. Opportunity engine explains fit for real jobs.
13. Application outcomes feed back into priorities.

## 5. Main screens

### Dashboard

-   Target role(s)
-   Market snapshot date and sample size
-   Readiness by role
-   Top critical gaps
-   Today's learning objective
-   Current certification progress
-   Interview readiness
-   Applications funnel
-   Data-quality warning banner when coverage is weak

### Market

-   Role demand by geography/time
-   Skill demand
-   Growth vs persistence
-   Skill co-occurrence
-   Seniority distribution
-   Education/language constraints
-   Source coverage and duplicate-removal statistics
-   Drill-down to supporting job records

### Skill Graph

-   Skill hierarchy and prerequisites
-   User evidence per skill
-   Market demand overlays
-   Canonical skill aliases
-   Taxonomy version

### Roadmap

Each item displays: - skill - why now - prerequisites - market
evidence - learner gap - expected hours - required artifact/evidence -
English objective - assessment gate - dependencies blocking progression

### Learn

Learning unit stages: 1. Why 2. Intuition 3. Concrete example 4. Formal
definition 5. Mathematics 6. Code 7. Production trade-offs 8. Technical
English 9. Sentence parsing 10. Listening 11. Recall 12. Explain in
English 13. Debugging 14. System design 15. Interview 16. Evidence
artifact

Not every skill requires every stage; templates are skill-type
dependent.

### Interview

-   text or voice
-   role and difficulty
-   technical correctness
-   completeness
-   answer structure
-   English clarity
-   terminology/chunks
-   follow-up questions
-   evidence-backed feedback
-   no unsupported personality/confidence inference

### Projects

-   project purpose
-   market skills covered
-   architecture
-   milestones
-   tests
-   deployment
-   evaluation metrics
-   GitHub evidence
-   interview story

### Certifications

-   mapped certification objectives
-   skill coverage overlap
-   missing prerequisites
-   practice results
-   recommendation rationale
-   status/accessibility notes

### Opportunities

-   role fit
-   critical requirements
-   preferred requirements
-   missing skills
-   education/language constraints
-   evidence matches
-   explanation and source date

### Applications

-   company/role
-   CV version
-   date/stage
-   interview stages
-   outcome
-   notes/feedback
-   skills involved

## 6. MVP

MVP contains: - job ingestion for a small approved source set, - raw and
normalized job storage, - deduplication, - role/skill extraction, -
canonical taxonomy, - market dashboard, - learner profile, - evidence
graph, - explainable gap engine, - 24-week roadmap generator.

MVP explicitly excludes: - autonomous applications, - automated CV
submission, - voice interview, - multi-agent orchestration, - complex
recommendation ML, - public marketplace, - social features.

## 7. Product metrics

Market: - unique jobs after dedupe - source coverage - extraction
precision/recall/F1 - taxonomy unknown-rate - duplicate
precision/recall - percentage of claims traceable to job records

Learning: - pre/post gain - 3/14/30-day retention - transfer-task
performance - explanation quality - technical-English comprehension gain

Career: - qualified application rate - recruiter response rate -
interview conversion - technical-stage conversion - offer rate -
time-to-readiness by target role

System: - ingestion success rate - extraction cost/job - LLM
cost/user/week - API latency - background job failure rate

## 8. Product guardrails

-   Never fabricate market percentages.
-   Never infer a learner knows a skill solely because it appears on a
    CV.
-   Never reorder prerequisites only because a skill is trending.
-   Never label a skill obsolete without sufficient longitudinal data.
-   Never make autonomous applications in MVP.
-   Never store raw secrets/tokens in prompts or logs.
-   Never expose scraped personal data not necessary for labor-market
    analysis.
