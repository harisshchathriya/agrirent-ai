import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/authContext";
import { loginUser } from "../../services/authService";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const data = await loginUser(email, password);
      login(data.access_token);
      navigate("/dashboard");
    } catch (error) {
      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(234,179,8,0.18),_transparent_25%),linear-gradient(180deg,_#eff6ff_0%,_#f8fafc_100%)] px-4">
      <form
        onSubmit={handleLogin}
        className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white/90 p-8 shadow-xl"
      >
        <h1 className="mb-2 text-center text-3xl font-bold">
          Login
        </h1>

        <p className="mb-6 text-center text-slate-500">
          Access your live AgriRent AI dashboard.
        </p>

        <input
          type="email"
          placeholder="Email"
          className="mb-4 w-full rounded-xl border border-slate-200 p-3"
          value={email}
          onChange={(event) =>
            setEmail(event.target.value)
          }
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="mb-4 w-full rounded-xl border border-slate-200 p-3"
          value={password}
          onChange={(event) =>
            setPassword(event.target.value)
          }
          required
        />

        {error ? (
          <div className="mb-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        <button
          disabled={submitting}
          className="w-full rounded-xl bg-emerald-700 py-3 text-white transition hover:bg-emerald-800 disabled:bg-emerald-400"
        >
          {submitting ? "Signing In..." : "Login"}
        </button>

        <p className="mt-5 text-center">
          Don't have an account?{" "}
          <Link className="text-emerald-700" to="/register">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}
