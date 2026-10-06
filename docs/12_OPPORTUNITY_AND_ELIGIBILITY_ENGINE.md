# 12 --- Opportunity and Eligibility Engine

## Why separate eligibility from skill fit

A candidate can have 90% technical skill fit and still be ineligible
because of: - mandatory degree - mandatory German level - work
authorization/location - required professional years - security
clearance - mandatory domain license/certification

Therefore job fit is not one percentage.

## Output model

### Eligibility

PASS / UNCERTAIN / FAIL Dimensions: - geography/work authorization -
language - degree - years experience - mandatory certification/license -
onsite/travel constraint

### Capability fit

-   core technical skills
-   production evidence
-   domain knowledge
-   system design
-   English technical communication

### Preference fit

Nice-to-have requirements.

### Stretch level

-   realistic now
-   realistic with short gap
-   stretch
-   long-horizon
-   structurally ineligible at present

## Explainability

Every decision cites the exact requirement text and normalized
interpretation.

Examples: - "German C1 --- mandatory --- current evidence missing" -
"Kubernetes --- preferred --- missing; does not block application" -
"MSc or equivalent experience --- ambiguous; manual review recommended"

## Application decision policy

The system recommends: APPLY NOW / APPLY AFTER GAP / STRETCH APPLY / DO
NOT PRIORITIZE

The recommendation is rule-based and versioned. The LLM only explains
it.

## Feedback

Track which missing requirements correlate with: - no response -
recruiter screen rejection - technical rejection - offer

Do not infer causality from small samples. Display sample size and
uncertainty.
