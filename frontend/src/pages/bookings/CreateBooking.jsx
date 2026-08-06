import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import LoadingState from "../../components/LoadingState";
import ErrorState from "../../components/ErrorState";
import { AuthContext } from "../../context/authContext";
import { createBooking } from "../../services/bookingService";
import { getEquipmentById } from "../../services/equipmentService";
import { formatCurrency } from "../../utils/formatters";

export default function CreateBooking() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useContext(AuthContext);
  const today = new Date().toISOString().split("T")[0];
  const [equipment, setEquipment] = useState(null);
  const [booking, setBooking] = useState({
    start_date: "",
    end_date: "",
  });
  const [pageLoading, setPageLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    async function loadBookingEquipment() {
      setPageLoading(true);
      setError("");

      try {
        const data = await getEquipmentById(id);
        setEquipment(data);
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        setPageLoading(false);
      }
    }

    loadBookingEquipment();
  }, [id]);

  async function loadEquipment() {
    setPageLoading(true);
    setError("");

    try {
      const data = await getEquipmentById(id);
      setEquipment(data);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setPageLoading(false);
    }
  }

  function handleChange(event) {
    const { name, value } = event.target;

    setBooking((currentBooking) => ({
      ...currentBooking,
      [name]: value,
    }));
  }

  const isOwnEquipment =
    equipment &&
    currentUser &&
    equipment.owner_id === currentUser.id;

  const bookingBlockedMessage = !equipment
    ? ""
    : !equipment.availability
      ? "This equipment is currently unavailable for booking."
      : isOwnEquipment
        ? "You cannot book your own equipment."
        : "";

  async function handleSubmit(event) {
    event.preventDefault();

    if (bookingBlockedMessage) {
      setError(bookingBlockedMessage);
      return;
    }

    if (booking.start_date < today) {
      setError(`Start date cannot be before today (${today}).`);
      return;
    }

    if (booking.end_date <= booking.start_date) {
      setError("End date must be after the start date.");
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
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  }

  if (pageLoading) {
    return (
      <MainLayout>
        <LoadingState message="Loading equipment details..." />
      </MainLayout>
    );
  }

  if (error && !equipment) {
    return (
      <MainLayout>
        <ErrorState
          title="Unable to load booking form"
          message={error}
          onRetry={loadEquipment}
        />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <PageHeader
        title="Book Equipment"
        description="Choose your rental dates and create a booking using the live backend validation rules."
      />

      {equipment ? (
        <div className="mb-6 rounded-[2rem] border border-emerald-100 bg-white/90 p-6 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
            Equipment
          </p>
          <div className="mt-3 grid gap-4 md:grid-cols-[1fr_auto] md:items-start">
            <div>
              <h2 className="text-3xl font-bold text-slate-900">
                {equipment.name}
              </h2>
              <p className="mt-2 text-sm font-medium text-slate-500">
                {equipment.category}
              </p>
              <p className="mt-3 text-slate-600">
                {equipment.location}
              </p>
            </div>
            <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4">
              <p className="text-sm text-slate-500">Price Per Day</p>
              <p className="text-2xl font-bold text-emerald-700">
                {formatCurrency(equipment.price_per_day)}
              </p>
            </div>
          </div>
        </div>
      ) : null}

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
          disabled={loading || !!bookingBlockedMessage}
          className="mt-8 inline-flex min-w-44 justify-center rounded-xl bg-emerald-700 px-8 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:bg-emerald-400"
        >
          {loading
            ? "Booking..."
            : bookingBlockedMessage
              ? "Booking Unavailable"
              : "Book Now"}
        </button>
      </form>
    </MainLayout>
  );
}
