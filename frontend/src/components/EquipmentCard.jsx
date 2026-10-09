import { Link } from "react-router-dom";
import { FaMapMarkerAlt } from "react-icons/fa";
import StatusBadge from "./StatusBadge";
import EquipmentImage from "./EquipmentImage";
import { formatCurrency } from "../utils/formatters";

export default function EquipmentCard({ equipment }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-emerald-100 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
      <EquipmentImage
        src={equipment.imageUrl}
        alt={equipment.name}
        containerClassName="h-52"
        iconClassName="text-8xl text-emerald-700"
      />

      <div className="space-y-5 p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold leading-tight text-slate-900">
              {equipment.name}
            </h2>
            <p className="mt-1 text-sm font-medium text-slate-500">
              {equipment.category}
            </p>
          </div>
          <StatusBadge
            status={equipment.available ? "available" : "unavailable"}
            label={equipment.available ? "Available" : "Booked"}
          />
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-600">
          <FaMapMarkerAlt className="text-emerald-700" />
          <span>{equipment.location}</span>
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Price / Day
          </p>
          <p className="text-2xl font-bold text-emerald-700">
            {formatCurrency(equipment.price)}
          </p>
        </div>

        <Link
          to={`/equipment/details/${equipment.id}`}
          className="block w-full rounded-xl bg-emerald-700 px-4 py-3 text-center font-semibold text-white transition hover:bg-emerald-800"
        >
          View Details
        </Link>
      </div>
    </div>
  );
}
