import { useEffect, useMemo, useState } from "react";
import DashboardCard from "../../components/DashboardCard";
import ErrorState from "../../components/ErrorState";
import LoadingState from "../../components/LoadingState";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import {
  getMyBookings,
  getOwnerBookings,
} from "../../services/bookingService";
import { getEquipment } from "../../services/equipmentService";

export default function Dashboard() {
  const [equipment, setEquipment] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [ownerBookings, setOwnerBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    setError("");

    try {
      const [
        equipmentData,
        myBookingsData,
        ownerBookingsData,
      ] = await Promise.all([
        getEquipment(),
        getMyBookings(),
        getOwnerBookings(),
      ]);

      setEquipment(equipmentData);
      setMyBookings(myBookingsData);
      setOwnerBookings(ownerBookingsData);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  const bookingMap = useMemo(() => {
    const entries = [...myBookings, ...ownerBookings];
    return new Map(entries.map((booking) => [booking.id, booking]));
  }, [myBookings, ownerBookings]);

  const combinedBookings = [...bookingMap.values()];
  const activeBookings = combinedBookings.filter(
    (booking) => booking.status === "approved"
  ).length;
  const pendingRequests = ownerBookings.filter(
    (booking) => booking.status === "pending"
  ).length;
  const completedRentals = combinedBookings.filter(
    (booking) => booking.status === "completed"
  ).length;
  const availableEquipment = equipment.filter(
    (item) => item.availability
  ).length;

  return (
    <MainLayout>
      <PageHeader
        title="Dashboard"
        description="Live operational overview from the current backend data, combining equipment inventory with renter and owner booking activity."
      />

      {loading ? (
        <LoadingState message="Loading dashboard metrics..." />
      ) : error ? (
        <ErrorState
          title="Unable to load dashboard"
          message={error}
          onRetry={loadDashboardData}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-5">
            <DashboardCard
              title="Total Equipment"
              value={equipment.length}
              subtitle="Live equipment records"
              color="#059669"
            />
            <DashboardCard
              title="Available Equipment"
              value={availableEquipment}
              subtitle="Ready for new bookings"
              color="#16a34a"
            />
            <DashboardCard
              title="Active Bookings"
              value={activeBookings}
              subtitle="Approved rentals in progress"
              color="#0284c7"
            />
            <DashboardCard
              title="Pending Requests"
              value={pendingRequests}
              subtitle="Awaiting owner action"
              color="#d97706"
            />
            <DashboardCard
              title="Completed Rentals"
              value={completedRentals}
              subtitle="Finished booking cycles"
              color="#7c3aed"
            />
          </div>

          <div className="mt-12 rounded-[2rem] border border-white/60 bg-white/90 p-8 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900">
              Live Snapshot
            </h2>

            <p className="mt-4 max-w-3xl leading-8 text-slate-600">
              The dashboard now reflects current backend state instead of placeholder counts. Equipment availability, booking approvals, and completion metrics update directly from the API responses.
            </p>
          </div>
        </>
      )}
    </MainLayout>
  );
}
