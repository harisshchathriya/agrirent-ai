import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/authContext";
import {
  loginUser,
  registerUser,
} from "../../services/authService";

export default function Register() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    setFormData((currentData) => ({
      ...currentData,
      [event.target.name]: event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await registerUser(formData);
      const auth = await loginUser(
        formData.email,
        formData.password
      );
      login(auth.access_token);
      navigate("/dashboard");
    } catch (error) {
      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(234,179,8,0.18),_transparent_25%),linear-gradient(180deg,_#fefce8_0%,_#f8fafc_100%)] px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-2xl rounded-[2rem] border border-white/70 bg-white/90 p-8 shadow-xl"
      >
        <h1 className="mb-2 text-center text-3xl font-bold">
          Create Account
        </h1>
        <p className="mb-6 text-center text-slate-500">
          Register a live user account for AgriRent AI.
        </p>

        <div className="grid gap-4 md:grid-cols-2">
          <input
            name="name"
            placeholder="Full Name"
            value={formData.name}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 p-3"
            required
          />
          <input
            name="email"
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 p-3"
            required
          />
          <input
            name="phone"
            placeholder="Phone Number"
            value={formData.phone}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 p-3"
            required
          />
        </div>

        <input
          name="password"
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className="mt-4 w-full rounded-xl border border-slate-200 p-3"
          required
        />

        {error ? (
          <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        <button
          type="submit"
          disabled={submitting}
          className="mt-6 w-full rounded-xl bg-emerald-700 py-3 text-white transition hover:bg-emerald-800 disabled:bg-emerald-400"
        >
          {submitting ? "Creating Account..." : "Register"}
        </button>

        <p className="mt-5 text-center">
          Already have an account?{" "}
          <Link className="text-emerald-700" to="/">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
