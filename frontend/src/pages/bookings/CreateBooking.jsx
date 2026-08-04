import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import { createBooking } from "../../services/bookingService";

export default function CreateBooking() {
  const { id } = useParams();
  const navigate = useNavigate();
  const today = new Date().toISOString().split("T")[0];
  const [booking, setBooking] = useState({
    start_date: "",
    end_date: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setBooking((currentBooking) => ({
      ...currentBooking,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (booking.start_date < today) {
      setError(`Start date cannot be before today (${today}).`);
      return;
    }

    if (booking.end_date < booking.start_date) {
      setError("End date must be on or after the start date.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      await createBooking({
        equipment_id: id,
        start_date: booking.start_date,
        end_date: booking.end_date,
      });

      setSuccessMessage(
        "Booking created successfully. Redirecting to your bookings..."
      );

      setTimeout(() => {
        navigate("/bookings");
      }, 800);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <MainLayout>
      <PageHeader
        title="Book Equipment"
        description="Choose your rental dates and create a booking using the live backend validation rules."
      />

      <form
        onSubmit={handleSubmit}
        className="rounded-[2rem] border border-emerald-100 bg-white/90 p-8 shadow-sm"
      >
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label className="mb-2 block font-semibold text-slate-700">
              Start Date
            </label>

            <input
              type="date"
              name="start_date"
              value={booking.start_date}
              onChange={handleChange}
              min={today}
              required
              className="w-full rounded-xl border border-slate-200 p-3"
            />
          </div>

          <div>
            <label className="mb-2 block font-semibold text-slate-700">
              End Date
            </label>

            <input
              type="date"
              name="end_date"
              value={booking.end_date}
              onChange={handleChange}
              min={booking.start_date || today}
              required
              className="w-full rounded-xl border border-slate-200 p-3"
            />
          </div>
        </div>

        {successMessage ? (
          <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-700">
            {successMessage}
          </div>
        ) : null}

        {error ? (
          <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-700">
            {error}
          </div>
        ) : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-8 rounded-xl bg-emerald-700 px-8 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:bg-emerald-400"
        >
          {loading ? "Booking..." : "Book Now"}
        </button>
      </form>
    </MainLayout>
  );
}
