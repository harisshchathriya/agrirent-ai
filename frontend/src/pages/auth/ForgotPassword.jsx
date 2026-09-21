import { useState } from "react";
import { Link } from "react-router-dom";
import { requestPasswordReset } from "../../services/authService";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const response = await requestPasswordReset(email);
      setSuccess(response.message);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.18),_transparent_30%),linear-gradient(180deg,_#eff6ff_0%,_#f8fafc_100%)] px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white/90 p-8 shadow-xl">
        <h1 className="mb-2 text-center text-3xl font-bold">Forgot Password</h1>
        <p className="mb-6 text-center text-slate-500">Enter your email and we will prepare a password reset link if an account exists.</p>
        <input type="email" placeholder="Email" value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-xl border border-slate-200 p-3" required />
        {error ? <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}
        {success ? <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{success}</div> : null}
        <button disabled={submitting} className="mt-6 w-full rounded-xl bg-emerald-700 py-3 text-white transition hover:bg-emerald-800 disabled:bg-emerald-400">{submitting ? "Sending..." : "Send Reset Link"}</button>
        <p className="mt-5 text-center"><Link className="text-emerald-700" to="/login">Back to Login</Link></p>
      </form>
    </div>
  );
}
