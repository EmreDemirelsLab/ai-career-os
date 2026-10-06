# 05 --- Learning, English and Interview Engine

## 1. Pedagogical objective

Teach AI/ML deeply enough that the learner can: - understand the
concept, - derive/use relevant mathematics, - implement it, - debug
it, - make production trade-offs, - understand it in English, - explain
it clearly in English, - defend decisions in an interview.

## 2. Default learning sequence

`WHY -> INTUITION -> EXAMPLE -> FORMAL DEFINITION -> MATH -> CODE -> PRODUCTION -> ENGLISH -> RETRIEVAL -> TRANSFER -> INTERVIEW`

The sequence is configurable by skill type.

## 3. Turkish-to-English bridge

For cognitively heavy new topics: 1. build the concept in Turkish, 2.
preserve canonical English technical terms, 3. repeat the same concept
using English source material, 4. parse difficult sentences, 5.
summarize the speaker's main claim, 6. explain the concept in simple
English, 7. progress to professional technical English.

The system should gradually reduce Turkish scaffolding based on
performance, not calendar date.

## 4. Sentence architecture training

For technical sentences identify: - main subject - main verb -
object/complement - subordinate clauses - relative clauses - modifiers -
connectors - contrast/cause/condition - main claim

Goal: `English -> concept`, not permanent
`English -> Turkish -> concept`.

## 5. Technical chunks

Store phrases as contextual chunks, not isolated vocabulary: - deploy a
model to production - reduce memory requirements - freeze pretrained
weights - monitor model drift - trade off latency against accuracy - fit
the model into GPU memory

Each chunk links to: - skill - example sentences - listening examples -
learner usage attempts

## 6. Listening protocol

For short technical segments: 1. listen without subtitles, 2. state main
point, 3. listen with English subtitles/transcript, 4. inspect
structure/chunks, 5. listen again without subtitles, 6. answer a
conceptual question, 7. explain the segment.

Measure message comprehension, not word-perfect transcription.

## 7. Mastery gates

A learner does not master a skill by watching content.

Possible gates: - conceptual quiz - numerical/math task - coding
implementation - debugging task - production scenario - English
explanation - interview question - delayed recall

## 8. Spaced retrieval

Review modality changes over time: - Day 0: conceptual - Day 3: recall -
Day 7: application - Day 14: debugging/interview - Day 30:
transfer/system design

Intervals adapt to performance.

## 9. Interview engine

Personas: - recruiter - ML engineer - senior ML engineer - AI
architect - hiring manager - CTO-style system discussion

Question types: - theory - math - coding - debugging - ML system
design - LLM system design - project defense - behavioral - English
communication

## 10. Interview evaluation

Separate scores: - technical correctness - completeness - trade-off
reasoning - structure - terminology - English clarity - response
relevance

Do not infer personality, intelligence or psychological confidence.

For voice, measurable speech features may include: - pause rate - filler
frequency - fluency - answer structure

## 11. Project learning

Projects are generated from market-relevant skill bundles.

Each project must include: - business problem - architecture - data -
baseline - evaluation - tests - deployment - monitoring - cost
considerations - security considerations - README - architecture
diagram - interview narrative

## 12. Certification integration

Certification objectives map to canonical skills.

A certification track must show: - market overlap - prerequisite gaps -
exam objectives - hands-on evidence - practice results - exam readiness

AWS MLA-C02 should map to data preparation, model/foundation-model
development, deployment/orchestration, monitoring/security, plus
GenAI/RAG/agents where present in the official blueprint.

Vendor certification must never replace project/production evidence.

## 13. Daily session generator

Inputs: - roadmap - review queue - available time - learner fatigue
preference if explicitly provided - upcoming certification/interview -
recent failures

Output: - one primary technical objective - one English objective - one
retrieval task - one evidence-producing action where appropriate

Avoid fragmented daily plans with too many unrelated topics.
