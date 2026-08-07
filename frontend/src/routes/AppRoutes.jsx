import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

// Authentication
import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";

// Dashboard
import Dashboard from "../pages/dashboard/Dashboard";

// Equipment
import EquipmentList from "../pages/equipment/EquipmentList";
import EquipmentDetails from "../pages/equipment/EquipmentDetails";
import AddEquipment from "../pages/equipment/AddEquipment";

// Bookings
import MyBookings from "../pages/bookings/MyBookings";
import OwnerBookings from "../pages/bookings/OwnerBookings";
import CreateBooking from "../pages/bookings/CreateBooking";
import ProtectedRoute from "./ProtectedRoute";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Authentication */}
        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Equipment */}
        <Route
          path="/equipment"
          element={<EquipmentList />}
        />

        {/* Equipment Details */}
        <Route
          path="/equipment/details/:id"
          element={<EquipmentDetails />}
        />

        {/* Add Equipment */}
        <Route
          path="/equipment/add"
          element={
            <ProtectedRoute>
              <AddEquipment />
            </ProtectedRoute>
          }
        />

        {/* Farmer Bookings */}
        <Route
          path="/bookings"
          element={
            <ProtectedRoute>
              <MyBookings />
            </ProtectedRoute>
          }
        />

        {/* Create Booking */}
        <Route
          path="/bookings/create/:id"
          element={
            <ProtectedRoute>
              <CreateBooking />
            </ProtectedRoute>
          }
        />

        {/* Owner Panel */}
        <Route
          path="/owner"
          element={
            <ProtectedRoute>
              <OwnerBookings />
            </ProtectedRoute>
          }
        />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}
