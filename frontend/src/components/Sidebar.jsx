import {
  FaClipboardList,
  FaHome,
  FaSignOutAlt,
  FaTractor,
  FaUserCog,
} from "react-icons/fa";
import { useContext } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Sidebar() {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  const linkClass = ({ isActive }) =>
    `mx-3 my-1 flex items-center gap-3 rounded-xl px-6 py-4 transition ${
      isActive
        ? "bg-emerald-700 text-white"
        : "text-slate-700 hover:bg-emerald-50"
    }`;

  return (
    <aside className="min-h-screen w-72 border-r border-slate-200 bg-white shadow-lg">
      <div className="border-b border-slate-200 p-6 text-3xl font-bold text-slate-900">
        Menu
      </div>

      <nav className="mt-4 flex flex-col">
        <NavLink to="/dashboard" className={linkClass}>
          <FaHome />
          Dashboard
        </NavLink>

        <NavLink to="/equipment" className={linkClass}>
          <FaTractor />
          Equipment
        </NavLink>

        <NavLink to="/bookings" className={linkClass}>
          <FaClipboardList />
          My Bookings
        </NavLink>

        <NavLink to="/owner" className={linkClass}>
          <FaUserCog />
          Owner Panel
        </NavLink>

        <button
          type="button"
          onClick={handleLogout}
          className="mx-3 mt-6 flex items-center gap-3 rounded-xl px-6 py-4 text-left text-red-600 transition hover:bg-red-50"
        >
          <FaSignOutAlt />
          Logout
        </button>
      </nav>
    </aside>
  );
}
