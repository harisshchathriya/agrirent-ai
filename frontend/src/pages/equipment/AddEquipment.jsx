import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/PageHeader";
import MainLayout from "../../layouts/MainLayout";
import { createEquipment } from "../../services/equipmentService";

const initialFormData = {
  name: "",
  category: "",
  description: "",
  location: "",
  price_per_day: "",
};

export default function AddEquipment() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(initialFormData);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [submitError, setSubmitError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentFormData) => ({
      ...currentFormData,
      [name]: value,
    }));
    setErrors((currentErrors) => ({
      ...currentErrors,
      [name]: "",
    }));
    setSubmitError("");
    setSuccessMessage("");
  }

  function validateForm() {
    const nextErrors = {};

    if (!formData.name.trim()) {
      nextErrors.name = "Equipment name is required.";
    }

    if (!formData.category.trim()) {
      nextErrors.category = "Category is required.";
    }

    if (!formData.location.trim()) {
      nextErrors.location = "Location is required.";
    }

    if (!formData.description.trim()) {
      nextErrors.description = "Description is required.";
    }

    if (!formData.price_per_day || Number(formData.price_per_day) <= 0) {
      nextErrors.price_per_day =
        "Price per day must be greater than zero.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaving(true);
    setSubmitError("");

    try {
      await createEquipment({
        ...formData,
        name: formData.name.trim(),
        category: formData.category.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        price_per_day: Number(formData.price_per_day),
      });

      setSuccessMessage(
        "Equipment created successfully. Redirecting to the equipment list..."
      );
      setFormData(initialFormData);

      setTimeout(() => {
        navigate("/equipment");
      }, 900);
    } catch (error) {
      setSubmitError(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <MainLayout>
      <PageHeader
        title="Add Equipment"
        description="Create a new equipment listing with validated backend-backed data."
      />

      <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <form
          onSubmit={handleSubmit}
          className="rounded-[2rem] border border-emerald-100 bg-white/90 p-8 shadow-sm"
        >
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block font-semibold text-slate-700">
                Equipment Name
              </label>
              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Mahindra Tractor"
                required
                className="w-full rounded-xl border border-slate-200 p-3 outline-none transition focus:border-emerald-500"
              />
              {errors.name ? (
                <p className="mt-2 text-sm text-rose-600">
                  {errors.name}
                </p>
              ) : null}
            </div>

            <div>
              <label className="mb-2 block font-semibold text-slate-700">
                Category
              </label>
              <input
                name="category"
                value={formData.category}
                onChange={handleChange}
                placeholder="Heavy"
                required
                className="w-full rounded-xl border border-slate-200 p-3 outline-none transition focus:border-emerald-500"
              />
              {errors.category ? (
                <p className="mt-2 text-sm text-rose-600">
                  {errors.category}
                </p>
              ) : null}
            </div>

            <div>
              <label className="mb-2 block font-semibold text-slate-700">
                Location
              </label>
              <input
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="Chennai"
                required
                className="w-full rounded-xl border border-slate-200 p-3 outline-none transition focus:border-emerald-500"
              />
              {errors.location ? (
                <p className="mt-2 text-sm text-rose-600">
                  {errors.location}
                </p>
              ) : null}
            </div>

            <div>
              <label className="mb-2 block font-semibold text-slate-700">
                Price Per Day
              </label>
              <input
                name="price_per_day"
                type="number"
                min="1"
                step="0.01"
                value={formData.price_per_day}
                onChange={handleChange}
                placeholder="3000"
                required
                className="w-full rounded-xl border border-slate-200 p-3 outline-none transition focus:border-emerald-500"
              />
              {errors.price_per_day ? (
                <p className="mt-2 text-sm text-rose-600">
                  {errors.price_per_day}
                </p>
              ) : null}
            </div>
          </div>

          <div className="mt-6">
            <label className="mb-2 block font-semibold text-slate-700">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the equipment, condition, and ideal use cases."
              rows={5}
              required
              className="w-full rounded-xl border border-slate-200 p-3 outline-none transition focus:border-emerald-500"
            />
            {errors.description ? (
              <p className="mt-2 text-sm text-rose-600">
                {errors.description}
              </p>
            ) : null}
          </div>

          {successMessage ? (
            <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-700">
              {successMessage}
            </div>
          ) : null}

          {submitError ? (
            <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-700">
              {submitError}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={saving}
            className="mt-8 w-full rounded-xl bg-emerald-700 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-emerald-400"
          >
            {saving ? "Saving Equipment..." : "Save Equipment"}
          </button>
        </form>

        <div className="rounded-[2rem] border border-emerald-100 bg-white/80 p-8 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
            Listing Tips
          </p>
          <h2 className="mt-3 text-3xl font-bold text-slate-900">
            Publish equipment renters can trust
          </h2>
          <div className="mt-6 space-y-4 text-slate-600">
            <p>
              Use a clear equipment name and category so renters can find the listing quickly in search and filters.
            </p>
            <p>
              Set an accurate daily price and describe condition, attachments, and ideal farming use cases.
            </p>
            <p>
              After saving, the listing appears immediately in the live equipment catalog and can be booked through the same backend APIs.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
