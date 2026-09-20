import { useContext } from "react";
import { FaTractor, FaUserCircle } from "react-icons/fa";
import { AuthContext } from "../context/authContext";

export default function Navbar() {
  const { currentUser } = useContext(AuthContext);

  return (
    <nav className="flex min-h-16 items-center justify-between border-b border-emerald-800/40 bg-emerald-700 px-8 text-white shadow-md">
      <div className="flex items-center gap-3">
        <FaTractor size={30} />
        <h1 className="text-3xl font-bold">
          AgriRent AI
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <FaUserCircle size={34} />
        <div className="text-right">
          <p className="font-semibold">
            {currentUser?.name || "Guest"}
          </p>
          <p className="text-sm uppercase tracking-wide text-emerald-100">
            {currentUser?.role || "Visitor"}
          </p>
        </div>
      </div>
    </nav>
  );
}
