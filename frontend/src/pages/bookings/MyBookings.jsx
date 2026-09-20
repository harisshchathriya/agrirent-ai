import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaCalendarAlt,
  FaEnvelope,
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
  cancelBooking,
  getMyBookings,
} from "../../services/bookingService";
import {
  formatCurrency,
  formatDate,
} from "../../utils/formatters";

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [activeBookingId, setActiveBookingId] = useState("");

  useEffect(() => {
    loadBookings();
  }, []);

  async function loadBookings() {
    setLoading(true);
    setError("");

    try {
      const data = await getMyBookings();
      setBookings(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(bookingId) {
    setActiveBookingId(bookingId);
    setActionError("");

    try {
      await cancelBooking(bookingId);
      await loadBookings();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setActiveBookingId("");
    }
  }

  return (
    <MainLayout>
      <PageHeader
        title="My Bookings"
        description="Review your live booking history with pricing, dates, and current approval status."
      />

      {actionError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-700">
          {actionError}
        </div>
      ) : null}

      {loading ? (
        <LoadingState message="Loading your bookings..." />
      ) : error ? (
        <ErrorState
          title="Unable to load bookings"
          message={error}
          onRetry={loadBookings}
        />
      ) : bookings.length === 0 ? (
        <EmptyState
          title="No bookings yet"
          description="Start by browsing available equipment and create your first rental."
        />
      ) : (
        <div className="space-y-5">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-sm transition hover:shadow-md"
            >
              <div className="flex flex-col justify-between gap-6 lg:flex-row">
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
                      <FaMapMarkerAlt />
                      {booking.location}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-start gap-4 lg:items-end">
                  <StatusBadge status={booking.status} />

                  <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4 lg:text-right">
                    <p className="text-sm text-slate-500">Total Price</p>
                    <p className="text-2xl font-bold text-emerald-700">
                      {formatCurrency(booking.total_price)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 grid gap-5 border-t border-slate-200 pt-6 md:grid-cols-3">
                <div className="flex items-center gap-3">
                  <FaCalendarAlt className="text-emerald-700" />

                  <div>
                    <p className="text-sm text-slate-500">Rental Period</p>

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
                  <p className="text-sm text-slate-500">Booking Status</p>
                  <div className="mt-2">
                    <StatusBadge status={booking.status} />
                  </div>
                </div>
              </div>

              {booking.owner_name || booking.owner_email ? (
                <div className="mt-6 rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4">
                  <p className="text-sm font-semibold text-emerald-800">
                    Equipment Owner
                  </p>

                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    {booking.owner_name ? (
                      <div className="flex items-center gap-3 text-slate-700">
                        <FaUser className="text-emerald-700" />
                        <div>
                          <p className="text-sm text-slate-500">Owner</p>
                          <p className="font-semibold">{booking.owner_name}</p>
                        </div>
                      </div>
                    ) : null}

                    {booking.owner_email ? (
                      <div className="flex items-center gap-3 text-slate-700">
                        <FaEnvelope className="text-emerald-700" />
                        <div>
                          <p className="text-sm text-slate-500">Owner Email</p>
                          <a
                            href={`mailto:${booking.owner_email}`}
                            className="font-semibold text-emerald-700 hover:text-emerald-800 hover:underline"
                          >
                            {booking.owner_email}
                          </a>
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
              ) : null}

              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  to={`/equipment/details/${booking.equipment_id}`}
                  className="inline-flex min-w-40 justify-center rounded-xl bg-emerald-700 px-6 py-3 font-semibold text-white transition hover:bg-emerald-800"
                >
                  View Equipment
                </Link>

                {booking.status === "pending" ? (
                  <button
                    type="button"
                    disabled={activeBookingId === booking.id}
                    onClick={() => handleCancel(booking.id)}
                    className="inline-flex min-w-40 justify-center rounded-xl bg-rose-600 px-6 py-3 font-semibold text-white transition hover:bg-rose-700 disabled:bg-rose-300"
                  >
                    {activeBookingId === booking.id ? "Cancelling..." : "Cancel Booking"}
                  </button>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </MainLayout>
  );
}
