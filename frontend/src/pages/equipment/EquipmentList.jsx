import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../../components/EmptyState";
import EquipmentCard from "../../components/EquipmentCard";
import ErrorState from "../../components/ErrorState";
import LoadingState from "../../components/LoadingState";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import { getEquipment } from "../../services/equipmentService";

export default function EquipmentList() {
  const [equipmentList, setEquipmentList] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [availability, setAvailability] = useState("all");
  const [sortByPrice, setSortByPrice] = useState("default");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadEquipment();
  }, []);

  async function loadEquipment() {
    setLoading(true);
    setError("");

    try {
      const data = await getEquipment();
      setEquipmentList(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  const categories = [
    "all",
    ...new Set(equipmentList.map((item) => item.category)),
  ];

  const filteredEquipment = equipmentList
    .filter((equipment) => {
      const query = search.trim().toLowerCase();
      const matchesSearch =
        !query ||
        equipment.name?.toLowerCase().includes(query) ||
        equipment.category?.toLowerCase().includes(query) ||
        equipment.location?.toLowerCase().includes(query);
      const matchesCategory =
        category === "all" || equipment.category === category;
      const matchesAvailability =
        availability === "all" ||
        String(equipment.availability) === availability;

      return (
        matchesSearch &&
        matchesCategory &&
        matchesAvailability
      );
    })
    .sort((left, right) => {
      if (sortByPrice === "low-high") {
        return left.price_per_day - right.price_per_day;
      }

      if (sortByPrice === "high-low") {
        return right.price_per_day - left.price_per_day;
      }

      return left.name.localeCompare(right.name);
    });

  return (
    <MainLayout>
      <PageHeader
        title="Equipment"
        description="Browse the live catalog, filter by availability, and move straight from discovery to booking."
        action={
          <Link
            to="/equipment/add"
            className="rounded-xl bg-emerald-700 px-6 py-3 font-semibold text-white shadow transition hover:bg-emerald-800"
          >
            + Add Equipment
          </Link>
        }
      />

      <div className="mb-8 grid gap-4 rounded-3xl border border-emerald-100 bg-white/90 p-5 shadow-sm lg:grid-cols-4">
        <input
          type="text"
          placeholder="Search by name, category or location"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500"
        />

        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500"
        >
          {categories.map((option) => (
            <option key={option} value={option}>
              {option === "all" ? "All Categories" : option}
            </option>
          ))}
        </select>

        <select
          value={availability}
          onChange={(event) => setAvailability(event.target.value)}
          className="rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500"
        >
          <option value="all">All Availability</option>
          <option value="true">Available</option>
          <option value="false">Booked</option>
        </select>

        <select
          value={sortByPrice}
          onChange={(event) => setSortByPrice(event.target.value)}
          className="rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500"
        >
          <option value="default">Sort by Name</option>
          <option value="low-high">Price: Low to High</option>
          <option value="high-low">Price: High to Low</option>
        </select>
      </div>

      {loading ? (
        <LoadingState message="Loading live equipment from the backend..." />
      ) : error ? (
        <ErrorState
          title="Unable to load equipment"
          message={error}
          onRetry={loadEquipment}
        />
      ) : filteredEquipment.length === 0 ? (
        <EmptyState
          title="No equipment matches these filters"
          description="Adjust the search or filter settings, or add a new equipment listing."
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredEquipment.map((equipment) => (
            <EquipmentCard
              key={equipment.id}
              equipment={{
                id: equipment.id,
                name: equipment.name,
                category: equipment.category,
                location: equipment.location,
                price: equipment.price_per_day,
                available: equipment.availability,
                imageUrl: equipment.image_url,
              }}
            />
          ))}
        </div>
      )}
    </MainLayout>
  );
}
