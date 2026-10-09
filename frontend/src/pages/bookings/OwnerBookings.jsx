import { useEffect, useState } from "react";
import {
  FaCalendarAlt,
  FaMapMarkerAlt,
  FaTractor,
  FaUser,
} from "react-icons/fa";
import EmptyState from "../../components/EmptyState";
import ErrorState from "../../components/ErrorState";
import LoadingState from "../../components/LoadingState";
import PageHeader from "../../components/PageHeader";
import StatusBadge from "../../components/StatusBadge";
import MainLayout from "../../layouts/MainLayout";
import {
  approveBooking,
  cancelOwnerBooking,
  completeBooking,
  getOwnerBookings,
  rejectBooking,
} from "../../services/bookingService";
import { getDemandTrends } from "../../services/aiService";
import { getDemandDisplayState } from "../../utils/equipmentPresentation";
import {
  formatCurrency,
  formatDate,
} from "../../utils/formatters";

export default function OwnerBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [activeBookingId, setActiveBookingId] = useState("");
  const [demandData, setDemandData] = useState(null);
  const [demandLoading, setDemandLoading] = useState(true);
  const [demandError, setDemandError] = useState("");
  const demandState = getDemandDisplayState(demandData);

  useEffect(() => {
    loadOwnerBookings();
    loadDemandTrends();
  }, []);

  async function loadDemandTrends() {
    setDemandLoading(true);
    setDemandError("");
    try {
      setDemandData(await getDemandTrends());
    } catch (requestError) {
      setDemandError(requestError.message);
    } finally {
      setDemandLoading(false);
    }
  }

  async function loadOwnerBookings() {
    setLoading(true);
    setError("");

    try {
      const data = await getOwnerBookings();
      setBookings(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(bookingId, action) {
    setActiveBookingId(bookingId);
    setActionError("");

    try {
      await action(bookingId);
      await loadOwnerBookings();
      // Approving or cancelling changes which bookings qualify as historical
      // demand, so the demand panel must be refreshed alongside the list.
      await loadDemandTrends();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setActiveBookingId("");
    }
  }

  function renderActions(booking) {
    const isSaving = activeBookingId === booking.id;

    if (booking.status === "pending") {
      return (
        <>
          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, approveBooking)}
            className="min-w-32 rounded-xl bg-emerald-700 px-5 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:bg-emerald-300"
          >
            {isSaving ? "Saving..." : "Approve"}
          </button>

          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, rejectBooking)}
            className="min-w-32 rounded-xl bg-rose-600 px-5 py-3 font-semibold text-white transition hover:bg-rose-700 disabled:bg-rose-300"
          >
            Reject
          </button>
        </>
      );
    }

    if (booking.status === "approved") {
      return (
        <>
          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, completeBooking)}
            className="min-w-32 rounded-xl bg-sky-600 px-5 py-3 font-semibold text-white transition hover:bg-sky-700 disabled:bg-sky-300"
          >
            {isSaving ? "Saving..." : "Complete"}
          </button>

          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, cancelOwnerBooking)}
            className="min-w-32 rounded-xl bg-slate-700 px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:bg-slate-300"
          >
            Cancel
          </button>
        </>
      );
    }

    return null;
  }

  function bookingDuration(booking) {
    const start = new Date(booking.start_date);
    const end = new Date(booking.end_date);
    return Math.round((end - start) / 86400000) + 1;
  }

  return (
    <MainLayout>
      <PageHeader
        title="Owner Dashboard"
        description="Manage incoming rental requests, move approved bookings to completion, and keep equipment availability in sync."
      />

      <section className="mb-8 rounded-3xl border border-violet-100 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-900">Demand Trend Intelligence</h2>
        <p className="mt-1 text-slate-600">Historical approved and completed bookings by equipment category.</p>
        {demandLoading ? (
          <p className="mt-4 text-slate-500">Loading historical demand...</p>
        ) : demandError ? (
          <div className="mt-4">
            <p role="alert" className="text-rose-700">{demandError}</p>
            <button type="button" onClick={loadDemandTrends} className="mt-2 font-semibold text-violet-700 hover:underline">Retry</button>
          </div>
        ) : (
          <>
            {demandState === "insufficient" ? (
              <p className="mt-4 rounded-xl bg-amber-50 p-3 text-amber-900">
                {demandData.message || "There is not enough consecutive monthly history to forecast demand."}
              </p>
            ) : demandState === "forecast" ? (
              <div className="mt-4 rounded-xl bg-sky-50 p-4 text-sky-950">
                <h3 className="font-semibold">Forecasted demand</h3>
                <p className="mt-1 text-sm">
                  {demandData.forecast_method?.replaceAll("_", " ")} · {demandData.forecast_horizon_months}-month horizon
                </p>
                {demandData.forecasts?.length ? (
                  <ul className="mt-3 space-y-1">
                    {demandData.forecasts.map((forecast) => (
                      <li key={`${forecast.category}-${forecast.period}`}>
                        {forecast.category}, {forecast.period}: {forecast.predicted_bookings} predicted booking(s)
                      </li>
                    ))}
                  </ul>
                ) : null}
                {demandData.evaluation ? (
                  <p className="mt-3 text-sm">
                    Chronological holdout ({demandData.evaluation.evaluation_start}–{demandData.evaluation.evaluation_end}, {demandData.evaluation.observations} months): moving-average MAE {demandData.evaluation.mae}; last-month baseline MAE {demandData.evaluation.baseline_mae}.
                  </p>
                ) : null}
                {demandData.limitations?.length ? (
                  <p className="mt-2 text-sm">Limitations: {demandData.limitations.join(" ")}</p>
                ) : null}
              </div>
            ) : demandState === "historical" ? (
              <p className="mt-4 rounded-xl bg-sky-50 p-3 text-sky-900">
                Historical counts are shown below; a forecast is not available in this response.
              </p>
            ) : null}
            {demandState !== "empty" && demandData?.categories?.length ? (
              <div className="mt-4 space-y-3">
                {demandData.categories.map((series) => (
                  <div key={series.category} className="rounded-xl border border-slate-200 p-4">
                    <h3 className="font-semibold text-slate-900">{series.category}</h3>
                    <p className="mt-1 text-sm text-slate-600">
                      {series.periods.map((period, index) => (
                        <span key={period} className="mr-3">{period}: {series.demand_counts[index]} booking(s)</span>
                      ))}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-slate-600">No approved or completed booking history is available yet.</p>
            )}
          </>
        )}
      </section>

      {actionError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-700">
          {actionError}
        </div>
      ) : null}

      {loading ? (
        <LoadingState message="Loading owner bookings..." />
      ) : error ? (
        <ErrorState
          title="Unable to load owner bookings"
          message={error}
          onRetry={loadOwnerBookings}
        />
      ) : bookings.length === 0 ? (
        <EmptyState
          title="No rental requests yet"
          description="Owner booking requests will appear here when renters submit them."
        />
      ) : (
        <div className="space-y-5">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-sm"
            >
              <div className="flex flex-col justify-between gap-6 xl:flex-row">
                <div className="flex gap-5">
                  <div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50">
                    <FaTractor className="text-5xl text-emerald-700" />
                  </div>

                  <div className="min-w-0">
                    <h2 className="text-2xl font-bold text-slate-900">
                      {booking.equipment_name}
                    </h2>

                    <p className="mt-1 text-sm font-medium text-slate-500">
                      {booking.category}
                    </p>

                    <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
                      <FaUser className="text-emerald-700" />
                      Customer: {booking.renter_name || "Renter"}
                    </div>

                    <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
                      <FaMapMarkerAlt className="text-emerald-700" />
                      {booking.location}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-start gap-4 xl:items-end">
                  <StatusBadge status={booking.status} />

                  <p className="rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4 text-sm text-slate-500 xl:text-right">
                    Total Price
                    <span className="mt-1 block text-2xl font-bold text-emerald-700">
                      {formatCurrency(booking.total_price)}
                    </span>
                  </p>
                </div>
              </div>

              <div className="mt-6 grid gap-5 border-t border-slate-200 pt-6 md:grid-cols-3">
                <div className="flex items-center gap-3">
                  <FaCalendarAlt className="text-emerald-700" />

                  <div>
                    <p className="text-sm text-slate-500">Booking Dates</p>

                    <p className="font-semibold">
                      {formatDate(booking.start_date)} - {formatDate(booking.end_date)}
                    </p>
                  </div>
                </div>

                <div>
                  <p className="text-sm text-slate-500">Price Per Day</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">
                    {formatCurrency(booking.price_per_day)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-500">Duration</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">
                    {bookingDuration(booking)} day{bookingDuration(booking) === 1 ? "" : "s"}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-500">Status</p>
                  <div className="mt-2">
                    <StatusBadge status={booking.status} />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                {renderActions(booking)}
              </div>
            </div>
          ))}
        </div>
      )}
    </MainLayout>
  );
}
