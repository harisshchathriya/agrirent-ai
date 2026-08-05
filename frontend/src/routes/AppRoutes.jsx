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
          element={<Navigate to="/" replace />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={<Dashboard />}
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
          element={<AddEquipment />}
        />

        {/* Farmer Bookings */}
        <Route
          path="/bookings"
          element={<MyBookings />}
        />

        {/* Create Booking */}
        <Route
          path="/bookings/create/:id"
          element={<CreateBooking />}
        />

        {/* Owner Panel */}
        <Route
          path="/owner"
          element={<OwnerBookings />}
        />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}
