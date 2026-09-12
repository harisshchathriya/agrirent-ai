import { useContext, useEffect, useState } from "react";
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
import { AuthContext } from "../../context/authContext";

export default function Dashboard() {
  const { currentUser } = useContext(AuthContext);
  const [equipment, setEquipment] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [ownerBookings, setOwnerBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
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
          currentUser?.role === "owner"
            ? getOwnerBookings()
            : Promise.resolve([]),
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

    loadDashboardData();
  }, [currentUser?.role, reloadToken]);

  const combinedBookings = Array.from(
    new Map(
      [...myBookings, ...ownerBookings].map((booking) => [
        booking.id,
        booking,
      ])
    ).values()
  );
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
  const bookedEquipment = equipment.length - availableEquipment;

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
          onRetry={() => setReloadToken((token) => token + 1)}
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

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                  Inventory
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">
                  {equipment.length} listings tracked
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                  Availability
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">
                  {availableEquipment} available, {bookedEquipment} booked
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                  Requests
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">
                  {pendingRequests} waiting for owner action
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                  Rentals
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">
                  {activeBookings} active, {completedRentals} completed
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </MainLayout>
  );
}
