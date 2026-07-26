import { useState } from "react";
import { User, Mail, Lock } from "lucide-react";
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

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSignup = async (e) => {
    e.preventDefault();

    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const response = await apiClient.post("/api/auth/register", {
        name: form.name,
        email: form.email,
        password: form.password,
      });

      alert(response.data.message);

      navigate("/login");
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Registration failed. Please try again."
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex justify-center items-center">
      <div className="bg-slate-900 w-[450px] rounded-3xl shadow-2xl p-10">

        <h1 className="text-4xl font-bold text-center text-blue-500">
          AI MISINFO
        </h1>

        <p className="text-center text-gray-400 mt-3">
          Create Your Account
        </p>

        <form onSubmit={handleSignup} className="space-y-5 mt-8">

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <User className="text-gray-400" />
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={form.name}
              onChange={handleChange}
              required
              className="bg-transparent outline-none w-full p-4 text-white"
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Mail className="text-gray-400" />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={form.email}
              onChange={handleChange}
              required
              className="bg-transparent outline-none w-full p-4 text-white"
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Lock className="text-gray-400" />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
              className="bg-transparent outline-none w-full p-4 text-white"
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Lock className="text-gray-400" />
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              value={form.confirmPassword}
              onChange={handleChange}
              required
              className="bg-transparent outline-none w-full p-4 text-white"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 py-4 rounded-xl font-bold text-white transition"
          >
            Create Account
          </button>

        </form>

        <p className="text-center text-gray-400 mt-6">
          Already have an account?
        </p>

        <div className="text-center mt-2">
          <Link
            to="/login"
            className="text-blue-400 hover:underline"
          >
            Login
          </Link>
        </div>

      </div>
    </div>
  );
}