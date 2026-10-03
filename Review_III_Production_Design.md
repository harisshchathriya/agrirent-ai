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

For a farmer without approved or completed booking history, the system will use a clearly labeled popularity fallback:

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

The fallback is not presented as personalized history. If there are no qualifying historical bookings at all, the service returns a safe empty or neutral result rather than inventing a preference.

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

The initial baseline requires a minimum of **3 historical periods**. Three periods do not guarantee reliable forecasting; they are only a minimum gate for evaluating whether a baseline can be attempted.

If fewer than three periods exist, the service will:

- not generate a forecast;
- return available historical demand information;
- return an explicit insufficient-history state; and
- not fabricate a prediction.

The threshold may be revisited after representative historical data becomes available.

## 12. Forecasting Strategy

The final forecasting algorithm is **not selected yet**. The Week 7 POC intentionally avoided selecting a complex forecasting model because the current database contains only one historical period.

After sufficient data becomes available, a lightweight forecasting baseline may be evaluated against the actual time series. LSTM, Prophet, XGBoost, Random Forest, TensorFlow, and PyTorch are not selected or promised by this design.

## 13. Proposed Backend Structure

The implemented Week 8 structure is:

```text
backend/app/
    api/
        ai_schema.py
    services/
        ai_recommendation_service.py
        ai_demand_service.py
    schemas/
        ai.py
```

Responsibilities:

- **Recommendation service:** authenticated farmer history, preference calculation, candidate retrieval, ranking, and explanations.
- **Demand service:** historical demand aggregation, category trends, historical-depth validation, and the future forecasting integration point.
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

The implemented Pydantic response schemas use these fields. Recommendation responses contain `recommendations`, `personalized`, `fallback_used`, and an optional message; each recommendation contains equipment ID, name, category, location, score, and explanation. Demand responses contain historical period count and labels, category demand series, forecast availability, status, insufficient-history state, and an optional message. Forecast values are omitted because the forecasting method remains undecided.

## 16. Frontend Integration Design

The existing React interface integrates the API responses without adding a separate page.

The farmer dashboard shows recommended equipment, category, location, explanation, relevance score, and a link to equipment details. The owner bookings interface shows historical category demand and the forecast state.

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
7. no forecast returned when history is insufficient.

API tests should cover authentication, authenticated farmer identity, invalid `limit`, response structure, and safe service-error handling. The implementation must add at least one or two Review-III-specific unit tests.

## 18. Database Strategy

The initial implementation will use the existing `users`, `equipment`, and `bookings` tables. No new database tables or migrations are planned. The schema will not be modified unless future implementation evidence demonstrates a real requirement.

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
| Cold-start fallback | Overall approved/completed equipment and category popularity | Provides a safe non-personalized fallback |
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

For recommendation, a production-ready deterministic baseline can be implemented using the current data structures. Historical approved and completed bookings will calculate farmer preferences independently of current availability. Available equipment will then be scored, sorted deterministically, and returned with explanations. Farmers without personal history will receive a clearly labeled popularity fallback.

For demand intelligence, historical category demand can be exposed now, but forecasting must remain guarded until sufficient historical periods exist. The current development database has only one historical month, so no forecasting model or accuracy claim is made.

The design prioritizes correctness, explainability, minimal complexity, safe integration, existing database reuse, testability, and production compatibility.
