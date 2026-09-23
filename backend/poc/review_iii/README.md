# Review-III Week 7 Proof of Concept

## 1. POC Objective

This isolated proof of concept inspects the available AgriRent AI booking and equipment data and establishes technically valid baselines for equipment recommendation and demand-trend analysis. It is not the production implementation and does not add API endpoints or change production behavior.

Run from the `backend` directory after configuring the existing `.env` file:

```text
python -m poc.review_iii.data_inspection
python -m poc.review_iii.recommendation_poc
python -m poc.review_iii.demand_poc
```

## 2. Actual Data Fields Used

The POC uses only fields confirmed in the existing SQLAlchemy models:

- `users.id`
- `equipment.id`, `equipment.category`, `equipment.availability`, `equipment.name`, and `equipment.location`
- `bookings.equipment_id`, `bookings.renter_id`, `bookings.start_date`, and `bookings.status`

Approved and completed bookings are treated as historical usage. Pending, rejected, and cancelled bookings are excluded from recommendation history and demand aggregation.

## 3. Data Availability Findings

The measured findings from the current development database are:

- Users: 4
- Equipment: 5
- Bookings: 13
- Historical bookings (approved/completed): 10
- Historical booking periods: 1 (`2026-08`)
- Booking status distribution: approved 2, cancelled 2, completed 8, rejected 1
- Equipment category distribution: Heavy 3, Soil Preparation 1, fertilizer 1
- Booking counts by category: Heavy 12, Soil Preparation 1
- All booking records by month: `2026-08` had 13 bookings.
- Historical demand bookings by month (approved/completed only): `2026-08` had 10 bookings.

## 4. Recommendation Baseline

The baseline filters equipment where `availability` is true. For a farmer with approved or completed booking history, it scores each available item as:

`category frequency * 2 + exact equipment frequency * 3`

Results are sorted deterministically by descending score, category, name, and ID. Each result includes the score and a frequency-based explanation. If the farmer has no historical usage, the same scoring structure falls back to overall historical popularity. No farmer location or other unsupported personalization signal is used.

## 5. Demand-Analysis Baseline

Approved and completed bookings are aggregated by booking `start_date` month and equipment category. The output includes the total historical series and recent category counts. A simple moving-average estimate over the latest three periods is produced only when at least three historical periods exist.

This moving average is a Week 7 baseline, not a selected production model.

## 6. Data Limitations

The POC does not assume a dataset size, user profile attributes, crop information, weather, soil information, GPS data, income, fuel usage, or equipment operating hours. Sparse history may prevent meaningful demand prediction. Empty data and insufficient historical periods are reported without fabricating forecast results.

## 7. Observed Results

The current development database contains 13 bookings across 4 users and 5 equipment records. Ten bookings are approved or completed and therefore used as historical usage. All 10 qualifying historical bookings occur in one month (`2026-08`), with 9 in the Heavy category and 1 in Soil Preparation. Three equipment records were available when the recommendation POC ran; the sample farmer with qualifying history produced available-item recommendations, but the single-period history does not support a demand forecast.

No accuracy, precision, recall, forecast-accuracy, revenue, or business-impact values are inferred.

## 8. Proposed Production Approach

The recommendation baseline can inform a later service that filters available equipment, ranks candidates from farmer usage history, supplies a fallback for cold-start farmers, and returns explainable results. The demand baseline can inform a later service that validates data sufficiency before returning category-level demand trends.

## 9. What Remains Undecided

The final recommendation implementation, demand prediction algorithm, feature refresh strategy, persistence strategy, API response contract, and frontend presentation remain undecided until the POC findings and production constraints are reviewed.

## 10. Next Implementation Steps

1. Review the measured data availability and limitations.
2. Select production-safe feature definitions and historical status rules.
3. Evaluate the baseline against representative development data.
4. Add focused tests for ranking, availability filtering, cold-start behavior, and insufficient demand history.
5. Design the future API and frontend integration separately from this POC.