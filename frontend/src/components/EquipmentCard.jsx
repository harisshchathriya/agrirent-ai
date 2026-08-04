import { Link } from "react-router-dom";
import { FaMapMarkerAlt, FaTractor } from "react-icons/fa";
import StatusBadge from "./StatusBadge";
import { formatCurrency } from "../utils/formatters";

export default function EquipmentCard({ equipment }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-emerald-100 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
      <div className="flex h-52 items-center justify-center bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50">
        {equipment.imageUrl ? (
          <img
            src={equipment.imageUrl}
            alt={equipment.name}
            className="h-full w-full object-cover"
          />
        ) : (
          <FaTractor className="text-8xl text-emerald-700" />
        )}
      </div>

      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              {equipment.name}
            </h2>
            <p className="mt-1 text-slate-500">
              {equipment.category}
            </p>
          </div>
          <StatusBadge
            status={equipment.available ? "available" : "unavailable"}
            label={equipment.available ? "Available" : "Booked"}
          />
        </div>

        <div className="mt-5 flex items-center gap-2 text-slate-600">
          <FaMapMarkerAlt className="text-emerald-700" />
          <span>{equipment.location}</span>
        </div>

        <div className="mt-6">
          <p className="text-sm text-slate-500">
            Price / Day
          </p>
          <p className="text-3xl font-bold text-emerald-700">
            {formatCurrency(equipment.price)}
          </p>
        </div>

        <Link
          to={`/equipment/details/${equipment.id}`}
          className="mt-8 block w-full rounded-xl bg-emerald-700 py-3 text-center font-semibold text-white transition hover:bg-emerald-800"
        >
          View Details
        </Link>
      </div>
    </div>
  );
}
