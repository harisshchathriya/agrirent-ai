import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
  const { currentUser, authLoading } = useContext(AuthContext);
  const [equipment, setEquipment] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [ownerBookings, setOwnerBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [errorTitle, setErrorTitle] = useState("Unable to load dashboard");
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    async function loadDashboardData() {
      if (authLoading || !currentUser) {
        setLoading(authLoading);
        return;
      }

      setLoading(true);
      setError("");
      setErrorTitle("Unable to load dashboard");

      try {
        const [equipmentData, myBookingsData] = await Promise.all([
          getEquipment().catch((requestError) => {
            throw new Error(
              `Equipment data: ${requestError.message}`,
              { cause: requestError }
            );
          }),
          getMyBookings().catch((requestError) => {
            throw new Error(
              `Your booking data: ${requestError.message}`,
              { cause: requestError }
            );
          }),
        ]);

        let ownerBookingsData = [];

        if (currentUser.role === "owner") {
          try {
            ownerBookingsData = await getOwnerBookings();
          } catch (requestError) {
            throw new Error(
              `Incoming owner bookings: ${requestError.message}`,
              { cause: requestError }
            );
          }
        }

        setEquipment(equipmentData);
        setMyBookings(myBookingsData);
        setOwnerBookings(ownerBookingsData);
      } catch (error) {
        const status = error.cause?.cause?.response?.status ||
          error.cause?.response?.status;

        setErrorTitle(
          status === 401 || status === 403
            ? "Authentication failed"
            : error.message.startsWith("Incoming owner bookings:")
              ? "Unable to load owner bookings"
              : "Unable to load dashboard"
        );
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, [authLoading, currentUser, reloadToken]);

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
  const isOwner = currentUser?.role === "owner";
  const dashboardEquipment = isOwner
    ? equipment.filter((item) => item.owner_id === currentUser.id)
    : equipment;
  const dashboardAvailableEquipment = dashboardEquipment.filter(
    (item) => item.availability
  ).length;
  const pendingBookings = myBookings.filter(
    (booking) => booking.status === "pending"
  ).length;
  const upcomingBookings = myBookings.filter(
    (booking) =>
      ["pending", "approved"].includes(booking.status) &&
      new Date(booking.start_date) >= new Date()
  );
  const completedBookings = myBookings.filter(
    (booking) => booking.status === "completed"
  ).length;
  const ownerRevenue = ownerBookings
    .filter((booking) => booking.status === "completed")
    .reduce((total, booking) => total + Number(booking.total_price || 0), 0);
  const quickActions = isOwner
    ? [
        ["Add Equipment", "/equipment/add"],
        ["My Equipment", "/equipment"],
        ["Booking Requests", "/owner"],
      ]
    : [
        ["Find Equipment", "/equipment"],
        ["My Bookings", "/bookings"],
      ];

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
          title={errorTitle}
          message={error}
          onRetry={() => setReloadToken((token) => token + 1)}
        />
      ) : (
        <>
          <div className="mb-8 flex flex-wrap gap-3">
            {quickActions.map(([label, path]) => (
              <Link
                key={label}
                to={path}
                className="rounded-xl bg-slate-900 px-5 py-3 font-semibold text-white transition hover:bg-slate-700"
              >
                {label}
              </Link>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-5">
            <DashboardCard
              title={isOwner ? "My Equipment" : "Total Equipment"}
              value={dashboardEquipment.length}
              subtitle={isOwner ? "Owner listings" : "Live equipment records"}
              color="#059669"
            />
            <DashboardCard
              title="Available Equipment"
              value={dashboardAvailableEquipment}
              subtitle="Ready for new bookings"
              color="#16a34a"
            />
            <DashboardCard
              title={isOwner ? "Total Bookings" : "Active Bookings"}
              value={isOwner ? ownerBookings.length : activeBookings}
              subtitle={isOwner ? "Bookings on your equipment" : "Approved rentals in progress"}
              color="#0284c7"
            />
            <DashboardCard
              title={isOwner ? "Pending Requests" : "Pending Bookings"}
              value={isOwner ? pendingRequests : pendingBookings}
              subtitle={isOwner ? "Awaiting your action" : "Awaiting owner action"}
              color="#d97706"
            />
            <DashboardCard
              title={isOwner ? "Completed Rentals" : "Completed Bookings"}
              value={isOwner ? completedRentals : completedBookings}
              subtitle={isOwner ? "Finished booking cycles" : "Your finished rentals"}
              color="#7c3aed"
            />
          </div>

          {!isOwner && currentUser?.role === "farmer" ? (
            <div className="mt-8 rounded-3xl border border-sky-100 bg-sky-50 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900">Upcoming Rentals</h2>
                  <p className="mt-1 text-slate-600">Your next approved or pending rental activity.</p>
                </div>
                <Link to="/bookings" className="font-semibold text-sky-700 hover:underline">View history</Link>
              </div>
              {upcomingBookings.length === 0 ? (
                <p className="mt-5 text-slate-600">You have no upcoming rentals yet.</p>
              ) : (
                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  {upcomingBookings.slice(0, 3).map((booking) => (
                    <div key={booking.id} className="rounded-2xl bg-white p-4">
                      <p className="font-semibold text-slate-900">{booking.equipment_name}</p>
                      <p className="mt-1 text-sm text-slate-500">{booking.start_date} to {booking.end_date}</p>
                      <p className="mt-2 text-sm capitalize text-sky-700">{booking.status}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}

          {isOwner ? (
            <div className="mt-8 grid gap-5 md:grid-cols-2">
              <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-6">
                <p className="text-sm uppercase tracking-[0.16em] text-emerald-700">Revenue</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{ownerRevenue.toLocaleString("en-IN", { style: "currency", currency: "INR" })}</p>
                <p className="mt-1 text-sm text-slate-600">Completed bookings only</p>
              </div>
              <div className="rounded-3xl border border-amber-100 bg-amber-50 p-6">
                <p className="text-sm uppercase tracking-[0.16em] text-amber-700">Utilization</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{dashboardEquipment.length ? Math.round(((dashboardEquipment.length - dashboardAvailableEquipment) / dashboardEquipment.length) * 100) : 0}%</p>
                <p className="mt-1 text-sm text-slate-600">Current unavailable share of your listings</p>
              </div>
            </div>
          ) : null}

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
                  {equipment.length === 0
                    ? "No equipment listed yet"
                    : `${equipment.length} listings tracked`}
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
                  {isOwner
                    ? ownerBookings.length === 0
                      ? "No incoming bookings"
                      : `${pendingRequests} waiting for owner action`
                    : "Owner requests are not part of this dashboard"}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                  Rentals
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">
                  {combinedBookings.length === 0
                    ? "No bookings yet"
                    : `${activeBookings} active, ${completedRentals} completed`}
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </MainLayout>
  );
}
