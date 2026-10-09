# Review-III Enhancement Proposal

## 1. Enhancement Title

**AI-Powered Equipment Recommendation and Demand Trend Prediction**

## 2. Approved AI/DS Specialization

The approved AI/DS specialization is:

> "AI model to recommend equipment based on usage patterns and predict demand trends."

The Review-III enhancement is designed specifically to implement this approved specialization within the existing AgriRent AI agricultural equipment rental marketplace.

## 3. Existing System Context

AgriRent AI is an agricultural equipment rental marketplace. Farmers can browse agricultural equipment and create rental bookings. Equipment owners can list and manage equipment. Booking information is stored in PostgreSQL.

The current system does not yet provide AI-powered equipment recommendations or AI-powered demand-trend prediction. The Review-III enhancement will extend the existing system while preserving its current rental workflow.

## 4. Problem Statement

Equipment discovery currently depends on a farmer manually browsing available equipment. This can make it harder for a farmer to identify equipment relevant to previous usage patterns.

The system already stores historical booking information, but that information is not currently converted into personalized equipment recommendations or demand-trend insights. Converting the available booking history into these capabilities can make equipment discovery more useful and can give owners clearer visibility into demand patterns within the rental platform.

No numerical business impact is assumed at the proposal stage.

## 5. Proposed Enhancement

### 5.1 Equipment Recommendation

The system will analyze historical booking and usage patterns associated with farmers and equipment. Potential signals available from the current database include:

- `renter_id`
- `equipment_id`
- equipment category
- equipment location
- booking dates
- booking status
- booking frequency derived from historical bookings

The system will filter currently available equipment, rank relevant candidates, and return the top recommendations for a farmer. Recommendations should be explainable so that a farmer can understand why an item was selected.

For example, a possible explanation is: "A similar equipment category was frequently used in your previous bookings." This is an example explanation and is not a commitment to a final production wording.

### 5.2 Demand Trend Prediction

The system will aggregate historical booking information by equipment, equipment category, and time period. It will use the resulting historical demand patterns to estimate future demand trends.

The final machine-learning or statistical prediction algorithm will not be selected in advance. The appropriate prediction approach will be chosen after evaluating the available data during the proof of concept.

## 6. Available Data

The current system provides the following relevant data domains:

- users
- equipment
- bookings

Booking history can be transformed into AI/DS features such as booking counts, booking frequency, category usage, equipment usage, location relationships, booking status filters, and time-based demand aggregates.

This proposal does not assume the availability of crop type, farm size, weather, soil type, GPS coordinates, income, fuel usage, or equipment operating hours, because these fields are not part of the known current system domain.

## 7. Proposed AI/DS Approach

### Equipment Recommendation

The initial proof of concept will:

1. Extract historical booking data.
2. Calculate farmer-equipment and farmer-category usage patterns.
3. Identify frequently used categories and equipment.
4. Filter currently available equipment.
5. Rank candidate equipment.
6. Return the top recommendations.

The recommendation approach will be evaluated during the proof of concept before the final production implementation is selected. A fallback based on overall popularity may be used where a farmer has insufficient personal history.

### Demand Prediction

The proof of concept will:

1. Aggregate historical bookings by time period and equipment category.
2. Create a demand time series.
3. Inspect the available data volume and patterns.
4. Establish a simple baseline.
5. Evaluate a suitable prediction approach.
6. Select the final approach based on proof-of-concept results.

No specific model, including Random Forest, XGBoost, LSTM, Prophet, TensorFlow, or PyTorch, has been selected at this stage.

## 8. Technology Choice

The proposed lightweight Python AI/DS stack may include:

- pandas
- scikit-learn
- NumPy, if required

Lightweight libraries are appropriate for this capstone because they support easier deployment and testing, reduce infrastructure complexity, and are suitable for tabular and time-series booking data.

These packages will not be installed and `requirements.txt` will not be modified during the proposal task.

## 9. Planned Architecture

The planned future architecture is:

```text
React Frontend
	|
	v
FastAPI API
	|
	v
AI/DS Service Layer
	|
	+----------------------+ 
	|                      |
	v                      v
Recommendation Logic     Demand Prediction Logic
	|                      |
	+----------+-----------+
		   |
		   v
	      PostgreSQL
	Users / Equipment / Bookings
```

The AI functionality will be integrated into the existing AgriRent AI backend rather than deployed as a separate product.

## 10. Planned API Design

The following are proposed API endpoints only. They will not be implemented during this proposal task.

### `GET /ai/recommendations`

Purpose: Return equipment recommendations for the authenticated farmer.

### `GET /ai/demand-trends`

Purpose: Return demand-trend information based on historical equipment booking data.

## 11. Planned Frontend Integration

These are future UI changes only.

For farmers, the existing application will gain a recommendation section showing recommended equipment and a simple explanation or relevance indicator.

For owners, an appropriate existing dashboard or page will provide demand-trend information and display equipment-category demand trends in a simple, understandable format.

No new pages will be created during this proposal task.

## 12. Proof of Concept

The Week 7 proof of concept will inspect real available booking data, determine whether sufficient historical data exists, create a small feature dataset, implement a baseline recommendation approach, implement a baseline demand-trend approach, evaluate the results, and document limitations. Its findings will guide selection of the production approach.

If the database has insufficient historical data, this limitation will be acknowledged. Controlled development or demonstration data may be required for model evaluation, while clearly distinguishing such data from real production history. The current dataset size is not assumed in this proposal.

## 13. Testing Strategy

The final implementation should include tests for the following areas.

### Recommendation

- valid farmer with booking history
- farmer with no booking history
- unavailable equipment filtering
- recommendation ranking
- empty recommendation result

### Demand Prediction

- valid historical data
- insufficient historical data
- empty booking dataset
- invalid category or input, if applicable

### API

- authentication
- response schema
- invalid requests
- error handling

At least one or two new unit tests will specifically target the Review-III enhancement, as required by the capstone. Existing Review-II functionality must continue to be covered by the existing test suite.

## 14. Deployment Plan

The enhancement must be integrated into the same AgriRent AI production application.

- The FastAPI backend will remain on the existing Render service.
- PostgreSQL will remain the existing production database.
- The React frontend will remain on the existing Vercel deployment.

No separate AI demo application will be created. Configuration will use environment variables where required, and no secrets may be committed.

## 15. Architecture Documentation

After implementation:

- the System Architecture diagram will be updated;
- the Module/Class diagrams will be updated if affected; and
- the API Contract/OpenAPI documentation will reflect the new endpoints.

The diagrams will not be modified during this proposal task.

## 16. Expected Outcome

The expected outcomes are:

- personalized equipment discovery;
- recommendations derived from actual booking and usage patterns;
- demand-trend visibility for equipment;
- explainable AI results;
- integration with the existing rental workflow; and
- production deployment inside the existing AgriRent AI application.

No accuracy, revenue, user-growth, or other numerical claims are made at this stage.

## 17. Scope Boundaries

This enhancement does not include:

- chatbot;
- weather prediction;
- crop disease detection;
- computer vision;
- payment prediction;
- fraud detection;
- external LLM services;
- unrelated recommendation systems;
- unrelated specializations;
- separate applications; or
- a major redesign of the Review-II rental workflow.

The enhancement must remain aligned with the approved AI/DS specialization.

## 18. Review-III Implementation Timeline

### Week 7

- enhancement research;
- proposal;
- proof of concept; and
- model or approach evaluation.

### Week 8

- full enhancement implementation;
- backend integration;
- frontend integration;
- unit testing; and
- production integration and deployment.

### Week 9

- final testing;
- UI polish;
- architecture documentation;
- README v3;
- CHANGELOG;
- demo video;
- production verification; and
- final Review-III preparation.

## 19. Risks and Mitigation

1. **Limited historical booking data** - Establish a baseline and use controlled development or demonstration data if necessary.
2. **Sparse user history** - Provide fallback or popularity-based recommendations.
3. **Sparse category demand history** - Use category-level aggregation and clearly label insufficient-data cases.
4. **Model complexity** - Start with interpretable, lightweight methods.
5. **Production latency** - Keep inference lightweight and avoid unnecessary model complexity.

## 20. Definition of Success

The enhancement will be successful when:

- recommendations can be generated from available usage and booking data;
- demand trends can be generated when sufficient historical data exists;
- insufficient-data cases are handled safely;
- AI functionality is exposed through the existing FastAPI application;
- frontend users can access the functionality;
- enhancement tests pass;
- existing Review-II functionality continues to work;
- the feature is deployed to the same production application; and
- documentation is updated.

## 21. Final Submission Implementation and Data Limitation

The implementation in this branch uses a deterministic frequency heuristic for recommendations, not a trained model. Its demand service supports a guarded three-month moving-average forecast for one month ahead after six continuous observed monthly periods, and reports chronological holdout MAE compared with a last-month naive baseline. The current local development snapshot has only one qualifying month (August 2026), so it correctly returns historical counts and `insufficient_history`; no forecast or real evaluation metric is claimed. The deployed Render API does not yet expose these AI routes.

Equipment image URLs are optional in equipment create/update requests and use the existing nullable `equipment.image_url` field. No schema migration was needed. A separate expired Render dataset is not represented by this local snapshot, and these findings must not be described as recovered production data.
