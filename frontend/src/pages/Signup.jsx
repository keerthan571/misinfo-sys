import { useState } from "react";
import { User, Mail, Lock } from "lucide-react";
import { Link } from "react-router-dom";

export default function Signup() {
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

  const handleSignup = (e) => {
    e.preventDefault();

    console.log(form);

    // Backend integration will be done later
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
              className="bg-transparent outline-none w-full p-4 text-white"
              onChange={handleChange}
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Mail className="text-gray-400" />
            <input
              type="email"
              name="email"
              placeholder="Email"
              className="bg-transparent outline-none w-full p-4 text-white"
              onChange={handleChange}
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Lock className="text-gray-400" />
            <input
              type="password"
              name="password"
              placeholder="Password"
              className="bg-transparent outline-none w-full p-4 text-white"
              onChange={handleChange}
            />
          </div>

          <div className="flex items-center bg-slate-800 rounded-xl px-4">
            <Lock className="text-gray-400" />
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              className="bg-transparent outline-none w-full p-4 text-white"
              onChange={handleChange}
            />
          </div>

          <button className="w-full bg-blue-600 hover:bg-blue-700 py-4 rounded-xl font-bold transition">
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