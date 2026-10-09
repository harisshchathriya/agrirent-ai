import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import EquipmentImage from "../../components/EquipmentImage";
import ErrorState from "../../components/ErrorState";
import LoadingState from "../../components/LoadingState";
import MainLayout from "../../layouts/MainLayout";
import PageHeader from "../../components/PageHeader";
import { getEquipmentById, updateEquipment } from "../../services/equipmentService";
import { validateOptionalImageUrl } from "../../utils/equipmentPresentation";

const emptyEquipment = {
  name: "",
  category: "",
  description: "",
  location: "",
  price_per_day: "",
  image_url: "",
};

export default function EditEquipment() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState(emptyEquipment);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [fieldError, setFieldError] = useState("");

  useEffect(() => {
    let active = true;
    getEquipmentById(id)
      .then((equipment) => {
        if (!active) return;
        setFormData({
          name: equipment.name,
          category: equipment.category,
          description: equipment.description,
          location: equipment.location,
          price_per_day: String(equipment.price_per_day),
          image_url: equipment.image_url || "",
        });
      })
      .catch((requestError) => active && setError(requestError.message))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [id]);

  function handleChange(event) {
    setFormData((current) => ({ ...current, [event.target.name]: event.target.value }));
    setFieldError("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const imageError = validateOptionalImageUrl(formData.image_url);
    if (imageError) {
      setFieldError(imageError);
      return;
    }
    const imageUrl = formData.image_url.trim();
    setSaving(true);
    setError("");
    try {
      await updateEquipment(id, {
        ...formData,
        name: formData.name.trim(),
        category: formData.category.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        price_per_day: Number(formData.price_per_day),
        image_url: imageUrl || null,
      });
      navigate(`/equipment/details/${id}`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <MainLayout><LoadingState message="Loading equipment for editing..." /></MainLayout>;
  }
  if (!formData.name && error) {
    return <MainLayout><ErrorState title="Unable to load equipment" message={error} onRetry={() => window.location.reload()} /></MainLayout>;
  }

  return (
    <MainLayout>
      <PageHeader title="Edit Equipment" description="Update your listing and keep its current image unless you change or clear the image URL." />
      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl rounded-[2rem] border border-emerald-100 bg-white/90 p-8 shadow-sm">
        <div className="grid gap-5 md:grid-cols-2">
          {[
            ["name", "Equipment Name", "text"],
            ["category", "Category", "text"],
            ["location", "Location", "text"],
            ["price_per_day", "Price Per Day", "number"],
          ].map(([name, label, type]) => (
            <div key={name}>
              <label htmlFor={`equipment-${name}`} className="mb-2 block font-semibold text-slate-700">{label}</label>
              <input
                id={`equipment-${name}`}
                name={name}
                type={type}
                min={type === "number" ? "0.01" : undefined}
                step={type === "number" ? "0.01" : undefined}
                required
                value={formData[name]}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-emerald-500"
              />
            </div>
          ))}
        </div>
        <div className="mt-5">
          <label htmlFor="equipment-description" className="mb-2 block font-semibold text-slate-700">Description</label>
          <textarea id="equipment-description" name="description" rows={5} required value={formData.description} onChange={handleChange} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-emerald-500" />
        </div>
        <div className="mt-5">
          <label htmlFor="equipment-image-url" className="mb-2 block font-semibold text-slate-700">Equipment image (optional)</label>
          <input id="equipment-image-url" name="image_url" type="text" inputMode="url" maxLength={255} value={formData.image_url} onChange={handleChange} aria-describedby="equipment-image-help" aria-invalid={Boolean(fieldError)} placeholder="https://example.com/equipment.jpg" className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-emerald-500" />
          <p id="equipment-image-help" className="mt-2 text-sm text-slate-500">Keep the current URL to preserve the image, or clear it to remove the image.</p>
          {fieldError ? <p role="alert" className="mt-2 text-sm text-rose-600">{fieldError}</p> : null}
          <EquipmentImage src={formData.image_url.trim()} alt="Equipment image preview" containerClassName="mt-4 h-48 rounded-xl" />
        </div>
        {error ? <p role="alert" className="mt-5 rounded-xl bg-rose-50 p-4 text-rose-700">{error}</p> : null}
        <button type="submit" disabled={saving} className="mt-7 w-full rounded-xl bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-emerald-400">
          {saving ? "Saving changes..." : "Save Changes"}
        </button>
      </form>
    </MainLayout>
  );
}
