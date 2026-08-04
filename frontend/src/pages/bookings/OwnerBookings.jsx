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
  cancelBooking,
  completeBooking,
  getOwnerBookings,
  rejectBooking,
} from "../../services/bookingService";
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

  useEffect(() => {
    loadOwnerBookings();
  }, []);

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
            className="rounded-xl bg-emerald-700 px-5 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:bg-emerald-300"
          >
            {isSaving ? "Saving..." : "Approve"}
          </button>

          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, rejectBooking)}
            className="rounded-xl bg-rose-600 px-5 py-3 font-semibold text-white transition hover:bg-rose-700 disabled:bg-rose-300"
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
            className="rounded-xl bg-sky-600 px-5 py-3 font-semibold text-white transition hover:bg-sky-700 disabled:bg-sky-300"
          >
            {isSaving ? "Saving..." : "Complete"}
          </button>

          <button
            type="button"
            disabled={isSaving}
            onClick={() => handleAction(booking.id, cancelBooking)}
            className="rounded-xl bg-slate-700 px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:bg-slate-300"
          >
            Cancel
          </button>
        </>
      );
    }

    return null;
  }

  return (
    <MainLayout>
      <PageHeader
        title="Owner Dashboard"
        description="Manage incoming rental requests, move approved bookings to completion, and keep equipment availability in sync."
      />

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
        <div className="space-y-6">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-sm"
            >
              <div className="flex flex-col justify-between gap-8 xl:flex-row">
                <div className="flex gap-6">
                  <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50">
                    <FaTractor className="text-6xl text-emerald-700" />
                  </div>

                  <div>
                    <h2 className="text-2xl font-bold text-slate-900">
                      {booking.equipment_name}
                    </h2>

                    <div className="mt-3 flex items-center gap-2 text-slate-600">
                      <FaUser className="text-emerald-700" />
                      Customer: {booking.renter_name || "Customer"}
                    </div>

                    <div className="mt-3 flex items-center gap-2 text-slate-600">
                      <FaMapMarkerAlt className="text-emerald-700" />
                      {booking.location}
                    </div>

                    <p className="mt-4 text-sm text-slate-500">
                      Price Per Day
                    </p>

                    <p className="text-xl font-semibold text-emerald-700">
                      {formatCurrency(booking.price_per_day)}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-start gap-5 xl:items-end">
                  <StatusBadge status={booking.status} />

                  <p className="text-right text-sm text-slate-500">
                    Total Price
                    <span className="mt-1 block text-2xl font-bold text-emerald-700">
                      {formatCurrency(booking.total_price)}
                    </span>
                  </p>
                </div>
              </div>

              <div className="mt-8 grid gap-6 border-t border-slate-200 pt-6 md:grid-cols-2">
                <div className="flex items-center gap-3">
                  <FaCalendarAlt className="text-emerald-700" />

                  <div>
                    <p className="text-sm text-slate-500">
                      Booking Start
                    </p>

                    <p className="font-semibold">
                      {formatDate(booking.start_date)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <FaCalendarAlt className="text-emerald-700" />

                  <div>
                    <p className="text-sm text-slate-500">
                      Booking End
                    </p>

                    <p className="font-semibold">
                      {formatDate(booking.end_date)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-8 flex flex-wrap gap-4">
                {renderActions(booking)}
              </div>
            </div>
          ))}
        </div>
      )}
    </MainLayout>
  );
}
