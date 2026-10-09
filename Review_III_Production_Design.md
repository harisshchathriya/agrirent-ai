# Review-III Production Design

**AI-Powered Equipment Recommendation and Demand Trend Prediction**

## 1. Purpose

This document converts the Week 7 proof-of-concept findings into a controlled production implementation plan. It locks the architecture and implementation decisions for Review-III before production work begins.

The enhancement is limited to the approved AI/DS specialization and does not change the existing Review-II rental workflow.

## 2. Approved Enhancement Scope

The approved specialization is:

> "AI model to recommend equipment based on usage patterns and predict demand trends."

The scope contains exactly two capabilities:

1. **Equipment Recommendation**
2. **Demand Trend Intelligence**

No unrelated AI capability is included.

## 3. Current System Baseline

The confirmed current system provides:

- farmer registration and login;
- owner registration and login;
- equipment listing;
- equipment browsing;
- the existing booking workflow;
- PostgreSQL persistence;
- an existing FastAPI service layer; and
- an existing React frontend.

Before Review-III implementation, the API modules covered authentication, equipment, bookings, and equipment relations, with schemas for users, equipment, bookings, equipment images, and reviews. Review-III adds an AI router and response schemas while preserving these existing routes and models.

## 4. Week 7 POC Findings

The Week 7 POC used the actual development database and measured:

- 4 users;
- 5 equipment records;
- 13 total bookings;
- 2 approved bookings;
- 8 completed bookings;
- 2 cancelled bookings;
- 1 rejected booking;
- 10 qualifying historical usage bookings; and
- 1 historical month: August 2026 (`2026-08`).

Approved and completed bookings are considered historical usage and demand. Pending, rejected, and cancelled bookings are excluded. The current development database does not contain enough historical periods for meaningful demand forecasting.

The POC established a deterministic, explainable recommendation baseline using category frequency multiplied by 2 plus exact equipment frequency multiplied by 3. It also established a popularity fallback for farmers without personal history. No forecasting model or forecasting accuracy was claimed.

## 5. Production Architecture

```text
React Frontend
        |
        v
FastAPI API
        |
        v
AI/DS Service Layer
        |
        +---------------------------+
        |                           |
        v                           v
Recommendation Service      Demand Trend Service
        |                           |
        +-------------+-------------+
                      |
                      v
                 PostgreSQL
             Users / Equipment /
                 Bookings
```

The AI functionality will remain inside the existing AgriRent AI application. No separate AI application and no external AI API are planned.

## 6. Recommendation Production Design

```text
Authenticated farmer
        |
        v
Identify authenticated farmer
        |
        v
Load historical approved/completed bookings
        |
        v
Calculate usage preferences
        |
        v
Load currently available equipment
        |
        v
Score candidate equipment
        |
        v
Sort deterministically
        |
        v
Return top-N recommendations
        |
        v
Frontend displays explanation
```

Historical preference calculation must not be restricted to equipment that is currently available. The implementation will first calculate farmer, category, and equipment frequency from all approved and completed bookings. It will then load the current candidate pool where `equipment.availability == true`, score only those candidates using the historical preferences, sort them, and return the top-N results.

Therefore, historically used equipment still contributes to preference calculation even when it is currently unavailable. Current availability is a candidate filter, not a historical-data filter.

## 7. Recommendation Scoring Design

The Week 7 baseline is the initial production baseline, not a sophisticated machine-learning model:

```text
score = (category relevance * 2) + (exact equipment relevance * 3)
```

- **Category relevance** is how often the farmer historically used the candidate's equipment category.
- **Exact equipment relevance** is how often the farmer historically used the candidate equipment.
- **Current availability** is a hard filter; unavailable equipment must not appear in recommendations.

Results may be sorted by score descending, category, equipment name, and equipment UUID. No unsupported personalization signal is introduced.

## 8. Cold-Start Recommendation Strategy

The system first scores available equipment from the authenticated farmer's
approved and completed bookings. It sets `personalized=true` only when that
history gives at least one available candidate a positive score. If the
farmer's history is absent or has no matching signal for available equipment,
the system may use overall popularity, setting `fallback_used=true` only when
that source gives at least one available candidate a positive score:

```text
Historical approved/completed bookings
        |
        v
Calculate category/equipment popularity
        |
        v
Filter currently available equipment
        |
        v
Rank available candidates
        |
        v
Return recommendations
```

The fallback is not presented as personalized history. If neither personal
history nor overall popularity yields a candidate signal, the service returns
neutral zero scores with an explanation rather than inventing a preference.

## 9. Explainability

Each recommendation should contain a simple explanation based on the score components. Examples include category usage relevance, previous exact equipment usage, and fallback popularity.

The implementation will not claim opaque explainability techniques such as SHAP or LIME unless they are actually implemented and evaluated later.

## 10. Demand Trend Production Design

```text
Historical bookings
        |
        v
Filter approved/completed
        |
        v
Aggregate by time period
        |
        v
Aggregate by equipment category
        |
        v
Check historical depth
        |
        +--------------------------+
        |                          |
Sufficient history       Insufficient history
        |                          |
        v                          v
Trend/forecast logic       Safe response
```

The current one-month dataset does not support a production forecasting claim. Historical demand information can still be exposed when available, but forecasting must remain guarded by the sufficiency rule in Section 11.

## 11. Demand Data Sufficiency Rule

The implemented baseline requires **6 consecutive monthly periods** after filling gaps between the first and last qualifying booking months with zero approved/completed bookings. Months outside that observed span are unknown and are not fabricated. Six months is an implementation gate, not a claim that the forecast is reliable.

If fewer than six periods exist, the service will:

- not generate a forecast;
- return available historical demand information;
- return an explicit insufficient-history state; and
- not fabricate a prediction.

The local development snapshot has one qualifying month, so it returns `insufficient_history` and no forecast. The threshold should be revisited only after representative history and evaluation results are available.

## 12. Forecasting Strategy

The production baseline is a **three-month moving average** for a one-month-ahead category forecast. It is evaluated chronologically over the latest three one-month holdout origins and compared with a last-month naive baseline; each origin uses only preceding observations. The current one-month database cannot run this evaluation or produce a forecast.

This simple baseline is not a trained model and its results must not be described as accurate without measured evidence. Seasonal models and complex ML libraries remain unselected.

## 13. Proposed Backend Structure

The implemented Week 8 structure is:

```text
backend/app/
    api/
    schemas/
        ai_schema.py
    services/
        ai_recommendation_service.py
        ai_demand_service.py
    schemas/
        ai.py
```

Responsibilities:

- **Recommendation service:** authenticated farmer history, preference calculation, candidate retrieval, ranking, and explanations.
- **Demand service:** continuous monthly aggregation, category trends, sufficiency validation, guarded moving-average forecasts, and chronological baseline evaluation.
- **AI API module:** authentication, request validation, service invocation, response serialization, and error handling.

The router is registered in the existing FastAPI application. It introduces no new tables or model fields.

## 14. Proposed API Contract

The existing FastAPI application implements the following authenticated endpoints.

### `GET /ai/recommendations`

Purpose: return recommendations for the authenticated farmer. Only farmers are authorized.

Authentication: JWT required.

Optional parameter: `limit`, bounded from 1 through 20.

The farmer identity must be derived from the authenticated JWT. The client must not provide an arbitrary `farmer_id` for recommendation lookup.

### `GET /ai/demand-trends`

Purpose: return category-level historical demand information and forecast state. Any authenticated user may access it.

Authentication: JWT required.

The initial contract should remain small and should expose an explicit insufficient-history state.

## 15. Proposed Response Concepts

Conceptual recommendation response fields:

- equipment ID;
- equipment name;
- category;
- location;
- score or relevance; and
- explanation.

Conceptual demand response fields:

- category;
- historical periods;
- demand counts;
- forecast availability or status; and
- forecast values only when sufficient history exists.

The implemented Pydantic response schemas use these fields. Recommendation responses contain `recommendations`, `personalized`, `fallback_used`, and an optional message; each recommendation contains equipment ID, name, category, location, score, and explanation. Demand responses also include forecast method, horizon, periods, category predictions, chronological evaluation MAE against a last-month baseline, status, limitations, and an optional message. Forecast values remain empty with `insufficient_history`.

## 16. Frontend Integration Design

The existing React interface integrates the API responses without adding a separate page.

The farmer dashboard shows heuristic recommendations, category, location, explanation, relevance score, and a link to equipment details. The owner bookings interface separates historical counts from forecast values, method, horizon, evaluation, and limitations.

When history is insufficient, the UI should show a clear message such as:

> Demand forecasting is unavailable because insufficient historical booking data is available.

The frontend must not show fake predictions.

## 17. Testing Strategy

Recommendation service tests should cover:

1. farmer with valid history;
2. farmer with no history;
3. unavailable equipment excluded;
4. historically used but currently unavailable equipment still contributing to preference;
5. category ranking;
6. exact equipment ranking;
7. deterministic ordering;
8. empty dataset; and
9. cold-start fallback.

Demand service tests should cover:

1. approved and completed bookings included;
2. cancelled and rejected bookings excluded;
3. category aggregation;
4. multiple historical periods;
5. fewer than three periods;
6. empty dataset; and
7. continuous monthly periods and zero-filled gaps;
8. no forecast returned when history is insufficient; and
9. chronological holdout evaluation that does not use future observations.

API tests should cover authentication, authenticated farmer identity, invalid `limit`, response structure, and safe service-error handling. The implementation must add at least one or two Review-III-specific unit tests.

## 18. Database Strategy

The initial implementation will use the existing `users`, `equipment`, and `bookings` tables. No new database tables or migrations are planned. The schema will not be modified unless future implementation evidence demonstrates a real requirement.

Equipment image URLs use the existing nullable `equipment.image_url` column. Create requests may omit the field; update requests preserve it when omitted and clear it only when null or blank is explicitly supplied. No database migration is required. Existing `equipment_images` relationships and cascade behavior are unchanged.

## 19. Dependency Strategy

The Week 7 POC required no new dependency. The initial production implementation should therefore use the existing Python and SQLAlchemy stack wherever practical.

Pandas or scikit-learn must not be added merely because this is an AI feature. Any future forecasting dependency must be documented and justified before installation. No dependency is added by this design task.

## 20. Security Design

- JWT authentication is required for the proposed endpoints.
- Authenticated farmer identity comes from the server-side authentication context.
- No arbitrary farmer ID is accepted for recommendation lookup.
- Responses do not expose passwords, password hashes, JWT secrets, tokens, or other sensitive user data.
- Existing authentication and authorization conventions are preserved.

## 21. Performance Design

The initial implementation will remain lightweight. It will avoid external API calls, large model inference, unnecessary background workers, unnecessary tables, and repeated full-database scans where avoidable.

PostgreSQL and existing service-layer patterns will be used. Query optimization can be revisited as production data grows. Recommendation ordering will remain deterministic.

## 22. Failure and Edge Cases

The production design defines safe handling for:

- no booking history;
- no available equipment;
- an empty equipment dataset;
- an empty booking dataset;
- insufficient demand history;
- an invalid limit;
- a database failure; and
- a service failure.

No state may result in fabricated AI output. Insufficient history is an expected analytical response, not an application crash or false forecast.

## 23. Deployment Design

The feature will be deployed inside the existing product:

- backend: the existing Render FastAPI service;
- database: the existing PostgreSQL database; and
- frontend: the existing Vercel React application.

No separate AI service or AI application is planned initially.

## 24. Architecture Documentation Impact

After implementation:

- the System Architecture diagram must be updated;
- the Module/Class diagram must be updated if affected; and
- API Contract/OpenAPI documentation will reflect the new endpoints.

Diagrams are not modified during this design task.

## 25. Implementation Roadmap

### Week 7

- proposal;
- POC; and
- production design.

### Week 8

- recommendation service;
- demand service;
- schemas;
- API;
- tests;
- frontend integration; and
- production deployment.

### Week 9

- final validation;
- UI polish;
- architecture documentation;
- README v3;
- CHANGELOG;
- demo video;
- production verification; and
- final Review-III preparation.

## 26. Decision Table

| Decision | Selected approach | Reason |
| --- | --- | --- |
| Historical booking statuses | Approved and completed only | Represent accepted or completed rental activity; exclude unsuccessful requests |
| Recommendation strategy | Deterministic frequency baseline | Explainable and supported by current booking data |
| Historical preference calculation | Calculate from all qualifying farmer bookings before availability filtering | Keeps historical preference separate from current candidate availability |
| Availability filtering | `equipment.availability == true` hard filter | Recommendations must contain currently available equipment only |
| Cold-start/no-match fallback | Overall approved/completed equipment and category popularity, only when it scores an available candidate positively | Flags identify the source that actually influences the candidate ranking; no signal yields neutral scores |
| Demand aggregation | Time period plus equipment category | Matches the approved demand-trend scope and current fields |
| Demand sufficiency threshold | Minimum of 3 historical periods | Prevents a forecast attempt with the current one-period dataset |
| Forecasting algorithm | Not selected yet | Current data is insufficient for model selection |
| Database changes | None initially | Existing users, equipment, and bookings are sufficient for the first implementation |
| Dependency strategy | Use the existing Python/SQLAlchemy stack | The POC required no additional dependency |
| Deployment strategy | Existing Render backend, PostgreSQL, and Vercel frontend | Keeps the feature inside the existing production application |

## 27. Non-Goals

The enhancement explicitly excludes:

- chatbot;
- weather prediction;
- crop disease detection;
- computer vision;
- payment prediction;
- fraud detection;
- external LLM services;
- unrelated AI features;
- unrelated specialization features;
- a separate AI application; and
- a major redesign of Review-II.

## 28. Final Design Summary

The proposed production architecture keeps Review-III inside the existing AgriRent AI application and reuses the current PostgreSQL users, equipment, and bookings data.

For recommendation, the implemented deterministic frequency baseline uses the
current data structures. Approved and completed bookings calculate farmer
preferences independently of current availability. Available equipment is
scored, sorted deterministically, and returned with explanations. The response
marks personalization only when personal history contributes a positive score
to an available candidate. Otherwise, overall popularity may be used and
explicitly marked as fallback; when neither source matches, neutral scores and
a no-match message are returned.

For demand intelligence, historical category demand can be exposed now, but forecasting must remain guarded until sufficient historical periods exist. The current development database has only one historical month, so no forecasting model or accuracy claim is made.

## 29. Final Submission Implementation Status

The implementation creates a continuous monthly series between the first and last approved/completed booking month, including zero-count gaps. It skips missing dates/categories and excludes pending, rejected, and cancelled bookings. When six months are available, it returns a one-month-ahead, per-category three-month moving-average baseline plus a chronological three-origin MAE comparison with the last-month naive baseline. This is a lightweight statistical baseline, not a trained model. The local development snapshot has one qualifying month, so it produces no forecast or real evaluation metric.

The read-only local database check for this submission found 13 bookings from 2026-08-04 through 2026-08-27. Ten approved/completed bookings occurred in 2026-08 (9 Heavy, 1 Soil Preparation). One month is insufficient, so the actual response reports `insufficient_history`, no prediction, and no real evaluation metric. Synthetic unit fixtures validate the branch and calculations but are not presented as business data.

Equipment create/update accepts an optional validated HTTP(S) `image_url`. Omitted update values preserve the stored URL; explicit null/blank clears it. The existing nullable model column and equipment-image relationship are unchanged. The owner UI supports editing, optional URL preview, and a shared fallback placeholder for missing or failed image URLs.

Initial pre-merge production smoke check (2026-10-09): frontend, `/health`, `/docs`, `/openapi.json`, equipment list/detail, and equipment-image GET requests returned HTTP 200. At that time, the deployed OpenAPI omitted the AI routes and direct requests returned HTTP 404. That observation predates the PR #5 and PR #6 deployment and is superseded by the post-merge verification below. No production writes were performed.

Post-merge release verification (2026-10-10): PR #5 and PR #6 are merged; the recommendation consistency fix (`d66fead`) is included in main commit `8779368`. GitHub Actions passed on that exact merged commit for backend tests, frontend tests, lint, and build. Render serves the merged application. Fresh read-only checks returned HTTP 200 for the frontend, `/health`, `/docs`, and `/openapi.json`. OpenAPI lists `/ai/recommendations` and `/ai/demand-trends`; unauthenticated requests to each returned HTTP 401, confirming that the routes are present and protected. Earlier authorized production requests returned HTTP 200 for both endpoints. The previous demand-trends response showed one observed month and insufficient history; no defensible forecast or accuracy result is claimed. The fresh checks did not repeat authenticated calls or access production records.

The design prioritizes correctness, explainability, minimal complexity, safe integration, existing database reuse, testability, and production compatibility.
