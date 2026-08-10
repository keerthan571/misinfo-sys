import { useState } from "react";
import { User, Mail, Lock, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSignup = async (e) => {
    e.preventDefault();

    if (
      !form.name ||
      !form.email ||
      !form.password ||
      !form.confirmPassword
    ) {
      alert("Please fill all fields");
      return;
    }

    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      const response = await apiClient.post(
        "/api/auth/register",
        {
          name: form.name,
          email: form.email,
          password: form.password,
        }
      );

      alert(
        response.data.message ||
        "Account created successfully 🎉"
      );

      navigate("/login");
    } catch (error) {
      console.error(error);
      alert(
        error.response?.data?.detail ||
        "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center px-4 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-blue-600/10 rounded-full blur-[140px]" />
        <div className="absolute top-0 right-0 w-[350px] h-[350px] bg-blue-500/5 rounded-full blur-[120px]" />
      </div>
      <div className="relative w-full max-w-[460px] bg-[#0f172a]/95 border border-slate-700/40 rounded-[24px] shadow-[0_25px_70px_rgba(0,0,0,0.5)] px-10 py-9 backdrop-blur-xl">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 rounded-xl bg-blue-600/15 border border-blue-500/20 flex items-center justify-center">
              <ShieldCheck className="text-blue-400" size={27} />
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-blue-500">
            AI MISINFO
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            AI-Powered Misinformation Intelligence
          </p>
        </div>
        <div className="mt-8">
          <h2 className="text-white text-2xl font-bold">
            Create your account
          </h2>
          <p className="text-slate-400 text-sm mt-2">
            Join the platform to analyze and track misinformation.
          </p>
          <div className="mt-5 border-t border-slate-700/50" />
        </div>
        <form
          onSubmit={handleSignup}
          className="space-y-5 mt-7"
        >
          <div>
            <label className="text-slate-300 text-sm font-medium">
              Full name
            </label>
            <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">
              <User
                className="text-slate-400 shrink-0"
                size={20}
              />
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
                autoComplete="name"
                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
              />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm font-medium">
              Email
            </label>
            <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">
              <Mail
                className="text-slate-400 shrink-0"
                size={20}
              />
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
                autoComplete="email"
                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
              />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm font-medium">
              Password
            </label>
            <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">
              <Lock
                className="text-slate-400 shrink-0"
                size={20}
              />
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                placeholder="Create a password"
                autoComplete="new-password"
                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
                className="shrink-0 w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white transition-colors rounded-lg"
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showPassword ? (
                  <EyeOff size={20} />
                ) : (
                  <Eye size={20} />
                )}
              </button>
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm font-medium">
              Confirm password
            </label>
            <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">
              <Lock
                className="text-slate-400 shrink-0"
                size={20}
              />
              <input
                type={
                  showConfirmPassword
                    ? "text"
                    : "password"
                }
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
                autoComplete="new-password"
                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
              />
              <button
                type="button"
                onClick={() =>
                  setShowConfirmPassword(
                    !showConfirmPassword
                  )
                }
                className="shrink-0 w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white transition-colors rounded-lg"
                aria-label={
                  showConfirmPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showConfirmPassword ? (
                  <EyeOff size={20} />
                ) : (
                  <Eye size={20} />
                )}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-xl py-4 font-semibold text-base transition-all duration-200 shadow-lg shadow-blue-600/15 hover:shadow-blue-500/25 hover:-translate-y-[1px] disabled:opacity-60 disabled:hover:translate-y-0 disabled:cursor-not-allowed"
          >
            {loading
              ? "Creating account..."
              : "Create account"}
          </button>
        </form>
        <div className="mt-7 pt-6 border-t border-slate-700/40 text-center">
          <p className="text-slate-500 text-sm">
            Already have an account?
          </p>
          <Link
            to="/login"
            className="inline-block mt-2 text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors"
          >
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}