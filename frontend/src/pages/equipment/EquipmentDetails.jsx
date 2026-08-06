import { useContext, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { FaMapMarkerAlt, FaTractor, FaUser } from "react-icons/fa";
import ErrorState from "../../components/ErrorState";
import LoadingState from "../../components/LoadingState";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import StatusBadge from "../../components/StatusBadge";
import { AuthContext } from "../../context/authContext";
import { getEquipmentById } from "../../services/equipmentService";
import { formatCurrency } from "../../utils/formatters";

export default function EquipmentDetails() {
  const { id } = useParams();
  const { currentUser } = useContext(AuthContext);
  const [equipment, setEquipment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadEquipmentDetails() {
      setLoading(true);
      setError("");

      try {
        const data = await getEquipmentById(id);
        setEquipment(data);
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        setLoading(false);
      }
    }

    loadEquipmentDetails();
  }, [id]);

  async function loadEquipment() {
    setLoading(true);
    setError("");

    try {
      const data = await getEquipmentById(id);
      setEquipment(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <MainLayout>
        <LoadingState message="Loading equipment details..." />
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <ErrorState
          title="Unable to load equipment"
          message={error}
          onRetry={loadEquipment}
        />
      </MainLayout>
    );
  }

  if (!equipment) {
    return (
      <MainLayout>
        <ErrorState
          title="Equipment not found"
          message="This equipment record is not available."
        />
      </MainLayout>
    );
  }

  const isOwnEquipment =
    currentUser &&
    equipment.owner_id === currentUser.id;
  const bookingBlockedMessage = !equipment.availability
    ? "This equipment is currently unavailable for booking."
    : isOwnEquipment
      ? "You cannot book your own equipment."
      : "";

  return (
    <MainLayout>
      <PageHeader
        title={equipment.name}
        description="Live equipment data from the backend, including booking availability and pricing."
      />

      <div className="grid gap-8 rounded-[2rem] border border-emerald-100 bg-white/90 p-6 shadow-sm lg:grid-cols-[1.1fr_0.9fr] lg:p-8">
        <div className="overflow-hidden rounded-[1.5rem] bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50">
          {equipment.image_url ? (
            <img
              src={equipment.image_url}
              alt={equipment.name}
              className="h-full min-h-[24rem] w-full object-cover"
            />
          ) : (
            <div className="flex min-h-[24rem] items-center justify-center">
              <FaTractor className="text-[7rem] text-emerald-700 lg:text-[8rem]" />
            </div>
          )}
        </div>

        <div className="flex flex-col">
          <h1 className="text-4xl font-bold text-slate-900 lg:text-5xl">
            {equipment.name}
          </h1>

          <p className="mt-3 text-lg font-semibold text-emerald-700">
            {equipment.category}
          </p>

          <p className="mt-6 text-base leading-8 text-slate-600">
            {equipment.description}
          </p>

          <div className="mt-8 grid gap-5 rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <div>
              <p className="text-sm text-slate-500">
                Price Per Day
              </p>
              <p className="text-4xl font-bold text-emerald-700">
                {formatCurrency(equipment.price_per_day)}
              </p>
            </div>

            <div className="flex items-center gap-3 text-slate-700">
              <FaMapMarkerAlt className="text-emerald-700" />
              {equipment.location}
            </div>

            <div className="flex items-center gap-3 text-slate-700">
              <FaUser className="text-emerald-700" />
              {equipment.owner_name || "Owner details unavailable"}
            </div>

            <div>
              <p className="mb-2 text-sm text-slate-500">Availability</p>
              <StatusBadge
                status={equipment.availability ? "available" : "unavailable"}
                label={equipment.availability ? "Available" : "Booked"}
              />
            </div>
          </div>

          {bookingBlockedMessage ? (
            <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-amber-800">
              {bookingBlockedMessage}
            </div>
          ) : (
            <Link
              to={`/bookings/create/${equipment.id}`}
              className="mt-8 inline-flex w-full justify-center rounded-xl bg-emerald-700 px-6 py-4 font-semibold text-white transition hover:bg-emerald-800 sm:w-auto sm:min-w-48"
            >
              Book Equipment
            </Link>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
